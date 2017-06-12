#!/usr/bin/env python

from requests import post
from optparse import OptionParser
from SoftLayer import VSManager, Client

parser = OptionParser()
parser.add_option("-s", "--server-name", dest="server_name", default=1)
parser.add_option("-c", "--cpu", dest="cpu", default=1)
parser.add_option("-e", "--env", dest="environment", default=None)
parser.add_option("-p", "--public-interface", dest="public_interface", default=False)
parser.add_option("-b", "--billing", dest="billing", default='hourly')
parser.add_option("-d", "--dedicated", dest="dedicated", default=False)
parser.add_option("-m", "--memory", dest="memory", default='1G')
parser.add_option("-t", "--disk-type", dest="disk_type", default='LOCAL')
parser.add_option("-v", "--primary-disk", dest="primary_disk", default=100)
parser.add_option("-z", "--disks", dest="custom_disk", default=None)
parser.add_option("-n", "--network", dest="network", default='1Gb')
parser.add_option("-q", "--quantity", dest="quantity", default=1)
parser.add_option("-i", "--image", dest="image", default='CentOS-7')
parser.add_option("-r", "--region", dest="datacenter", default='sao01')
parser.add_option("-l", "--local-only", dest="local_only", default=False)

(opt, args) = parser.parse_args()

sl_user   = 'YOUR_SOFTLAYER_USER'
sl_apikey = 'YOUR_SOFTLAYER_AKEY'

client = Client(username=sl_user,api_key=sl_apikey)
vs = VSManager(client)

def _str_to_bool(s):
    if s in ['True', 'true', 't', 1]:
        return True
    return False


config = {
    'domain': 'mydomain.com',
    'cpu': int(opt.cpu),
    'memory': str(opt.memory),
    'network': str(opt.network),
    'name': str(opt.server_name),
    'billing': str(opt.billing),
    'environment': str(opt.environment),
    'quantity': int(opt.quantity),
    'public_interface': _str_to_bool(opt.public_interface),
    'local_only': _str_to_bool(opt.local_only),
    'datacenter': str(opt.datacenter),
    'dedicated': _str_to_bool(opt.dedicated),
    'image': str(opt.image),
    'disk_type': str(opt.disk_type),
    'primary_disk': int(opt.primary_disk),
    'disk_advanced': str(opt.custom_disk)
}

environments = {
    'qa': {
        'env_id': 1,
        'sao01': {
            'pvt': {
                'vlan_id': 0
            },
            'pub': {
                'vlan_id': 0,
                'vlan_pub_id': 0
            }
        }
    },
    'preprod': {
        'env_id': 2,
        'sao01': {
            'pvt': {
                'vlan_id': 0
            },
            'pub': {
                'vlan_id': 0,
                'vlan_pub_id': 0
            }
        }
    },
    'production': {
        'env_id': 3,
        'sao01': {
            'pvt': {
                'vlan_id': 0
            },
            'pub': {
                'vlan_id': 0,
                'vlan_pub_id': 0
            }
        },
        'par01': {
            'pvt': {
                'vlan_id': 0
            },
            'pub': {
                'vlan_id': 0,
                'vlan_pub_id': 0
            }
        }
    }
}

images = {
    'CENTOS-7_64': 'CENTOS_7_64'
}

envs = environments[config['environment']]
dc_env = envs[config['datacenter']]

def _get_num_from_string(x):
    return int(''.join(n for n in x if n.isdigit()))


def _get_memory_size(gb):
    return _get_num_from_string(gb)*1024


def _get_network_length(gb):
    return _get_num_from_string(gb)*1000


def _get_billing_suffix():
    if config['billing'] == 'monthly':
        return 'n'
    return 's'


def _get_vsi_name():
    return '%s%s' % (config['name'], _get_billing_suffix())


def _get_next_id():
    _hostname = '%s%d*' % (_get_vsi_name(), envs['env_id'])
    idlist = []
    object_mask = 'mask[hostname]'
    vss = vs.list_instances(hostname=_hostname,
                      mask=object_mask)

    for v in vss: idlist.append(_get_num_from_string(v['hostname']))
    for a in range(1, 100):
        _id = '%d%02d' % (envs['env_id'], a)
        if int(_id) not in idlist:
            return _id


def _callback():
    # Implements here your callback
    pass


tags = [config['environment']]

for _i in range(0, config['quantity']):
    _hostname = '%s%s' % (_get_vsi_name(), _get_next_id())
    _all_disks = []
    new_vsi = {
        'domain': config['domain'],
        'hostname': '%s' % _hostname,
        'datacenter': config['datacenter'],
        'dedicated': config['dedicated'],
        'cpus': config['cpu'],
        'ssh_keys': [YOUR_SSH_KEY_ID],
        'memory': _get_memory_size(config['memory']),
        'nic_speed': _get_network_length(config['network']),
    }

    if isinstance(images[config['image']], int):
        new_vsi['image_id'] = images[config['image']]
    elif isinstance(images[config['image']], str):
        new_vsi['os_code'] = images[config['image']]
    else:
        new_vsi['os_code'] = 'CENTOS_7_64'


    if config['billing'] == 'monthly':
        new_vsi['hourly'] = False
    else:
        new_vsi['hourly'] = True


    if config['public_interface'] == True:
        new_vsi['private'] = False
        new_vsi['private_vlan'] = dc_env['pub']['vlan_id']
        new_vsi['public_vlan'] = dc_env['pub']['vlan_pub_id']
    else:
        new_vsi['private'] = True
        new_vsi['private_vlan'] = dc_env['pvt']['vlan_id']


    if config['disk_type'] == 'SAN':
        new_vsi['local_disk'] = False
    else:
        new_vsi['local_disk'] = True


    if config['primary_disk'] == 100:
        _all_disks.append(100)
    else:
        _all_disks.append(25)


    if config['disk_advanced'] != '':
        for d in config['disk_advanced'].split(','):
            _all_disks.append(d)

    new_vsi['disks'] = _all_disks


    if config['local_only'] == True:
        tags.append('softlayer-network-only')


    new_vsi['tags'] = ','.join(tags)

    print 'Creating Instance: %s' % _hostname

    vsi = vs.create_instance(**new_vsi)

    print 'Created Instance: %s (%d)' % (_hostname, int(vsi['id']))
    _callback()
    print '... Instance called-back'

