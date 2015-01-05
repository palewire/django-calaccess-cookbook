from __future__ import with_statement

import yaml
import time
from fabric.colors import green
from fabric.api import env, local, task

from amazon import createserver
from configure import configure
from chef import installchef, cook
from app import restartapache, rmpyc
from app import pipinstall, manage, migrate, collectstatic

env.user = 'ubuntu'
env.disable_known_hosts = True
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.app_user = 'ccdc'
env.project_dir = '/apps/calaccess/repo/'
env.activate = 'source /apps/calaccess/bin/activate'


@task
def bootstrap():
    """
    Install chef and use it to fully install the application on
    an Amazon EC2 instance.
    """
    # Fire up a new server
    id, host = createserver()

    # Add the new server's host name to the configuration file
    config = yaml.load(open('./config.yml', 'rb'))
    config['host'] = str(host)
    config_file = open('./config.yml', 'w')
    config_file.write(yaml.dump(config, default_flow_style=False))
    config_file.close()

    print "- Waiting 30 seconds before logging in to configure machine"
    time.sleep(30)

    # Install chef and run it
    installchef()
    cook()

    # Fire up the Django project
    migrate()
    collectstatic()
    restartapache()

    # Done deal
    print(green("Success!"))
    print "Visit the app at %s" % host


@task
def ssh():
    """
    Log into the EC2 instance using SSH.
    """
    local("ssh %s@%s -i %s" % (env.user, env.hosts[0], env.key_filename[0]))


__all__ = (
    'configure',
    'createserver',
    'installchef',
    'cook',
    'restartapache',
    'rmpyc',
    'pipinstall',
    'manage',
    'migrate',
    'collectstatic',
    'bootstrap',
    'ssh',
)
