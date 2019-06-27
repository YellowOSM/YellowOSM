#!/bin/bash
logfile=/var/log/yosm_downstream.log
backend_scripts=/root/docker-compose/responder/scripts

set -e
date >> $logfile 2>&1
pwd >> $logfile 2>&1
cd $backend_scripts
pwd >> $logfile 2>&1
cd osm2pgsql
bash ./cron_import_pbf.sh          >> $logfile 2>&1
date >> $logfile 2>&1
cd ..
python3 ./export_osm_to_elasticsearch.py     >> $logfile 2>&1
date >> $logfile 2>&1
bash ./elasticsearch_data_import.sh yosm     >> $logfile 2>&1
date >> $logfile 2>&1
bash ./elasticsearch_data_import.sh yosm_dev >> $logfile 2>&1
date >> $logfile 2>&1
