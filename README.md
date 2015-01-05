django-calaccess-bootstrap
==========================

A set of helpers for deploying CAL-ACCESS Django apps on Amazon Web Services

Prerequisites
-------------

* Python 2.7
* virtualenv
* git
* An account with Amazon Web Services to provision servers using EC2

Getting started
---------------

Create a virtualenv.

```bash
$ virtualenv django-calaccess-bootstrap
```

Jump in it.

```bash
$ cd django-calaccess-bootstrap
$ . bin/activate
```

Clone this repository.

```bash
$ git clone https://github.com/california-civic-data-coalition/django-calaccess-bootstrap.git repo
```

Jump in it and install the Python requirements.

```bash
$ cd repo
$ pip install -r requirements.txt
```

Use Fabric to spin up a server on Amazon EC2. Before it gets started it will
ask you to input your private credentials.

```bash
$ fab bootstrap
```
