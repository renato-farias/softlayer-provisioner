# softlayer-provisioner

It helps you to create VSI on Softlayer using only simple args.

After its execution, it will launch new VSI with the following template name:

Monthly VSI: name-of-your-instanceM101.yourdomain.com

or 

Hourly VSI: name-of-your-instanceS101.yourdomain.com


## Using

Edit the script and set your environment IDs, VLAN IDs and User/Key from your SoftLayer Account.

    python provisioner.py --server-name="NAME_OF_YOUR_INSTANCE" --cpu=1 --env="production" --public-interface=false --billing="hourly" --dedicated=false --memory="1gb" --disk-type="SAN" --primary-disk=100 --disks="" --network="1gb" --quantity=1 --image="CENTOS-7_64" --region="sao01" --local-only=false
