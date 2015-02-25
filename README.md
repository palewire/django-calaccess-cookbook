django-calaccess-cookbook
=========================

A Chef cookbook and Fabfile for deploying the California Civic Data Coalition's applications for analyzing the California Secretary of State’s CAL-ACCESS database on Amazon Web Services

Prerequisites
-------------

* Python 2.7
* virtualenv
* git

Getting started
---------------

Create a virtualenv.

```bash
$ virtualenv django-calaccess-cookbook
```

Jump in it.

```bash
$ cd django-calaccess-cookbook
$ . bin/activate
```

Clone this repository.

```bash
$ git clone https://github.com/california-civic-data-coalition/django-calaccess-cookbook.git repo
```

Jump in it and install the Python requirements.

```bash
$ cd repo
$ pip install -r requirements.txt
```

Starting a server on Amazon EC2
-------------------------------

Before you can spin up a server, you will an account with Amazon Web Services to use its EC2 service. If you don't have one already, you'll need to sign up [here](http://aws.amazon.com).

You'll also need to [create an key pair](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) and store it at ``~/.ec2/``. Then ensure your default security group is configured to allow SSH
access on port 22 and HTTP access on port 80.

Then use Fabric to spin up a server on Amazon EC2. Before it gets started it will
ask you to input your private credentials and some configuration options.

```bash
$ fab ec2bootstrap
```
