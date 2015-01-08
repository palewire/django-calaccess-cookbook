import time
import random
import boto.ec2
import boto.rds
from fabric.api import task, env
from configure import loadconfig


@task
def createrds(block_gb_size=12):
    """
    Spin up a new database backend with Amazon RDS.
    """
    loadconfig()

    print("Connecting to Amazon RDS")
    conn = boto.rds.connect_to_region(
        env.AWS_REGION,
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
    )

    print("- Reserving an database")
    db = conn.create_dbinstance(
        "ccdc-%s" % random.choice(range(0, 99)),
        block_gb_size,
        'db.%s' % env.EC2_INSTANCE_TYPE,
        'ccdc',     # Username
        'ccdcccdc'  # Password
    )

    # Check up on its status every so often
    print('- Waiting for instance to start')
    status = db.update()
    while status != 'available':
        time.sleep(10)
        status = db.update()
    db.modify(security_groups=[env.AWS_SECURITY_GROUP])

    return db.endpoint[0]


@task
def createserver(
    ami='ami-978dd9a7',
    block_gb_size=100
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
        instance_type=env.EC2_INSTANCE_TYPE,
        security_groups=(env.AWS_SECURITY_GROUP,),
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
    print("- Provisioned at: %s" % instance.public_dns_name)
    return (instance.id, instance.public_dns_name)
