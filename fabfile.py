from __future__ import with_statement

import os
import sys
import boto.ec2
import time
import random
from fabric.api import *
from fabric.colors import *
from fabric.contrib.project import rsync_project
from os.path import expanduser

pwd = os.path.dirname(__file__)
sys.path.append(pwd)

env.key_filename = (expanduser(''),)
env.user = 'ubuntu'
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.app_user = 'ccdc'
env.project_dir = '/apps/calaccess/repo/'
env.activate = 'source /apps/calaccess/bin/activate'
from secrets import *


def create_server(
    region='us-west-2',
    ami='ami-978dd9a7',
    instance_type='m1.medium',
    block_gb_size=12):
    """
    Spin up a new server on Amazon EC2.
    
    Returns the id and public address.
    
    By default, we use Ubuntu 12.04 LTS
    """
    print("Warming up...")
    conn = boto.ec2.connect_to_region(
        region,
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
    )
    print("Reserving an instance...")
    bdt = boto.ec2.blockdevicemapping.BlockDeviceType(connection=conn)
    bdt.size = block_gb_size
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping(connection=conn)
    bdm['/dev/sda1'] = bdt
    reservation = conn.run_instances(
        ami,
        key_name=env.key_name,
        instance_type=instance_type,
        security_groups=('mysql-dev',),
        block_device_map=bdm,
    )
    instance = reservation.instances[0]
    instance.add_tag("Name", "calaccess")
    print('Waiting for instance to start...')
    # Check up on its status every so often
    status = instance.update()
    while status == 'pending':
        time.sleep(10)
        status = instance.update()
    print(green("Instance state: %s" % instance.state))
    print(green("Public dns: %s" % instance.public_dns_name))
    return (instance.id, instance.public_dns_name)


def bootstrap():
    install_chef()
    cook()
    migrate()
    collectstatic()
    restart_apache()


def install_chef():
    """
    Install all the dependencies to run a Chef cookbook
    """
    # Install dependencies
    sudo('apt-get update', pty=True)
    sudo('apt-get install -y git-core ruby2.0 ruby2.0-dev', pty=True)
    # Screw ruby docs.
    sudo("echo 'gem: --no-ri --no-rdoc' > /root/.gemrc")
    sudo("echo 'gem: --no-ri --no-rdoc' > /home/ubuntu/.gemrc")
    # Install Chef
    sudo('curl -L https://www.chef.io/chef/install.sh | sudo bash', pty=True)


def cook():
    """
    Update Chef cookbook and execute it.
    """
    sudo('mkdir -p /etc/chef')
    sudo('chown ubuntu -R /etc/chef')
    rsync_project("/etc/chef/", "./chef/")
    sudo('cd /etc/chef && %s' % env.chef, pty=True)


def restart_apache():
    """
    Restarts apache on both app servers.
    """
    sudo("/etc/init.d/apache2 reload", pty=True)


def clean():
    """
    Erases pyc files from our app code directory.
    """
    env.shell = "/bin/bash -c"
    with cd(env.project_dir):
        sudo("find . -name '*.pyc' -print0|xargs -0 rm", pty=True)


def install_requirements():
    """
    Install the Python requirements.
    """
    _venv("pip install -r requirements.txt")


def migrate():
    """
    Run python manage.py migrate command
    """
    _venv("python manage.py migrate")


def collectstatic():
    """
    Roll out the latest static files
    """
    _venv("rm -rf ./static")
    _venv("python manage.py collectstatic --noinput")


def manage(cmd):
    _venv("python manage.py %s" % cmd)


def _venv(cmd):
    """
    A wrapper for running commands in our prod virturalenv
    """
    with cd(env.project_dir):
        sudo("%s && %s" % (env.activate, cmd), user=env.app_user)


def ssh():
    local("ssh ubuntu@%s -i %s" % (env.hosts[0], env.key_filename[0]))
