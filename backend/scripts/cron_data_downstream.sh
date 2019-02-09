#!/bin/bash
logfile=/var/log/yosm_downstream.log
backend_scripts=/root/docker-compose/responder/scripts

set -e
pwd >> $logfile 2>&1
cd $backend_scripts
pwd >> $logfile 2>&1
bash ./osm2pgsql/cron_import_pbf.sh >> $logfile 2>&1
python3 ./export_osm_to_elasticsearch.py >> $logfile 2>&1
bash ./elasticsearch_data_import.sh >> $logfile 2>&1
