#!/bin/bash
logfile=/var/log/yosm_downstream.log
# backend_scripts=/root/docker-compose/responder/scripts
backend_scripts=/root/backend/scripts/

echo PATH >> $logfile
echo $PATH >> $logfile
PATH=$PATH:/usr/local/bin

set -e
date >> $logfile 2>&1
pwd >> $logfile 2>&1
cd $backend_scripts
pwd >> $logfile 2>&1
cd osm2pgsql
bash ./cron_import_pbf.sh          >> $logfile 2>&1
date >> $logfile 2>&1
echo 'done with pbf import' >> $logfile 2>&1
cd $backend_scripts
cd ..
pwd
echo 'running pipenv install' >> $logfile 2>&1
# pipenv --bare install >> $logfile 2>&1
pipenv install >> $logfile 2>&1

cd scripts
date >> $logfile 2>&1
echo 'running export osm to elasticsearch' >> $logfile 2>&1
pipenv run python3 ./export_osm_to_elasticsearch.py --split  >> $logfile 2>&1
date >> $logfile 2>&1
## fail with dev index first :)
echo 'updating yosm_dev index' >> $logfile 2>&1
bash ./elasticsearch_data_import.sh yosm_dev >> $logfile 2>&1
date >> $logfile 2>&1
echo 'updating yosm index' >> $logfile 2>&1
bash ./elasticsearch_data_import.sh yosm     >> $logfile 2>&1
date >> $logfile 2>&1
echo "Done updating index..." >> $logfile 2>&1
