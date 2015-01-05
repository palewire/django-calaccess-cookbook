import time
import boto.ec2
from fabric.api import task, env
from configure import loadconfig


@task
def createserver(
    ami='ami-978dd9a7',
    instance_type='m1.medium',
    block_gb_size=12
):
    """
    Spin up a new Ubuntu 14.04 server on Amazon EC2.

    Returns the id and public address.
    """
    loadconfig()
    print("Connecting to Amazon EC2")
    conn = boto.ec2.connect_to_region(
        env.AWS_REGION,
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
    )
    print("- Reserving an instance")
    bdt = boto.ec2.blockdevicemapping.BlockDeviceType(connection=conn)
    bdt.size = block_gb_size
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping(connection=conn)
    bdm['/dev/sda1'] = bdt
    reservation = conn.run_instances(
        ami,
        key_name=env.key_name,
        instance_type=instance_type,
        #security_groups=('mysql-dev',),
        block_device_map=bdm,
    )
    instance = reservation.instances[0]
    instance.add_tag("Name", "calaccess")
    print('- Waiting for instance to start')
    # Check up on its status every so often
    status = instance.update()
    while status == 'pending':
        time.sleep(10)
        status = instance.update()
    print("- Live at: %s" % instance.public_dns_name)
    return (instance.id, instance.public_dns_name)
