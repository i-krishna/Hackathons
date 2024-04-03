# Parallelize Airflow tasks in Docker 

1. login to node, cd to /data/DIP-Overall-master/build/remote and run  
``` 
docker-compose -f docker-compose-dev.yaml up -d dip_workflow_dev
docker-compose -f docker-compose-dev.yaml up -d dip_core_dev
docker-compose -f docker-compose-dev.yaml up -d dip_metastore_dev
```
2. login to node for accessing dip_workflow_dev instance. 

# Paralleism settings

1. Login to dip_workflow_test container with ```docker exec -ti dip_workflow_test bash``` 
  
2. Install postgres within dip_workflow_dev docker container. Follow steps as shown below 
  ```
  sudo su - 
  yum install postgresql postgresql-server postgresql-devel postgresql-contrib postgresql-docs
  echo 'LC_ALL="en_US.UTF-8"' >> /etc/locale.conf
  sudo su -l postgres -c "postgresql-setup initdb"
  sudo service postgresql start
  sudo -u postgres psql
  CREATE DATABASE airflow;
  cd /var/lib/pgsql/data
  ```
  - Edit pg_hba.conf  to below settings
```
  # TYPE  DATABASE        USER            ADDRESS                 METHOD
# "local" is for Unix domain socket connections only
local   all             all                                     peer
# IPv4 local connections:
host    all             all             0.0.0.0/0               trust
# IPv6 local connections:
host    all             all             ::1/128                 md5
# Allow replication connections from localhost, by a user with the
# replication privilege.
#local   replication     postgres                                peer
#host    replication     postgres        127.0.0.1/32            ident
#host    replication     postgres        ::1/128                 ident
```
- Edit postgresql.conf to below settings
```
listen_addresses = ‘*’
port = 5432 
```

- sudo service postgresql restart

3. Configure airflow to use postgres instead of default sqlite
- cd /root/airflow 
- Edit airflow.cfg to below settings

```
sql_alchemy_conn = postgresql+psycopg2://postgres@localhost:5432/airflow
executor = localexecutor
```
- source /home/dipuser/dip_venv/bin/activate 
- Empty proxy to connec to internet to pip install a library with. (just to test: echo $http_proxy, echo $https_proxy)
  ```
    export http_proxy= 
    export https_proxy=
  ```
 - pip install psycopg2==2.7.5 --ignore-installed
 - airflow initdb
 
- airflow webserver (dip specific command - systemctl restart airflow_scheduler) 
- airflow scheduler (dip specific command - systemctl restart airflow_webserver) 
  
# Test parallelism

- within generated_code workflows of _INIT.py, _EXEC.py, edit concurrency=6 to start 6 tasks at a time in airflow as shown below

For INIT Workflow
```
dag = DAG('KPI_CALC_INIT',
default_args=default_args,
description='KPI_CALC_INIT',
schedule_interval=None,
concurrency=6)
```
For EXEC Workflow
```
dag = DAG('KPI_CALC_EXEC',
default_args=default_args,
description='KPI_CALC_EXEC',
schedule_interval=None,
concurrency=6)
```
- copy python workflow files with ```scp File*.py root@node:/data/docker_mounts/dev/dip_workflow/dag_data```
- Incase of Broken DAG: 'Variable NODE_ENV does not exist' error, click on Admin and Variables. Click on create and add
Name: NODE_ENV
Value: dev
- Turn on the init workflow and check code before trgiggering workflow to see paralleism of tasks

# Airflow reading materials

- https://airflow.apache.org/docs/stable/howto/initialize-database.html
- https://hub.docker.com/r/apache/airflow
- https://medium.com/@christo.lagali/implement-parallelism-in-airflow-375610219ba
- https://stackoverflow.com/questions/52214474/how-to-run-tasks-parallely-in-apache-airflow/56666711#56666711 

# Build docker image from harbour

```
docker-compose -f docker-compose-dev.yaml build --no-cache dip_workflow_test
docker-compose -f docker-compose-dev.yaml push dip_core_dev
docker-compose -f docker-compose-dev.yaml pull dip_core_dev
docker-compose -f docker-compose-dev.yaml up -d --force-recreate dip_core_dev
```
