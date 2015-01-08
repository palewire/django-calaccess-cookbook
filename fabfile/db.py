from configure import ConfigTask
from fabric.api import sudo, env, cd, task, get, local


@task(task_class=ConfigTask)
def dumpdb():
    sudo("mysqldump -u ccdc -pccdc ccdc | gzip > ccdc.sql.gz", pty=True)


@task(task_class=ConfigTask)
def getdb():
    get("ccdc.sql.gz", "ccdc.sql.gz")


@task(task_class=ConfigTask)
def loadrds():
    local("gunzip < ccdc.sql.gz | mysql -h %s ccdc -u ccdc -pccdcccdc" % env.host)
