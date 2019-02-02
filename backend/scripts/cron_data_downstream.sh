#!/bin/bash
set -e
logfile=/var/log/yosm_downstream.log
bash ./osm2pgsql/cron_import_pbf.sh >> $logfile 2>&1
python3 ./export_osm_to_elasticsearch.py >> $logfile 2>&1
bash ./elasticsearch_data_import.sh >> $logfile 2>&1
