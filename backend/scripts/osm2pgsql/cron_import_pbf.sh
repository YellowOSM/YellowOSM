#!/bin/sh

pbffile="/tmp/austria-current.osm.pbf"
state_url="http://download.geofabrik.de/europe/austria-updates/state.txt"
download_sub_path="https://download.geofabrik.de/europe/austria-"
# TODO:
# add
# http://download.geofabrik.de/europe/germany-latest.osm.pbf
# http://download.geofabrik.de/europe/switzerland-latest.osm.pbf
#
# or use DACH http://download.geofabrik.de/europe/dach-latest.osm.pbf
#download_sub_path="https://download.geofabrik.de/europe/dach-"
#
# http://download.geofabrik.de/europe/denmark-latest.osm.pbf
# http://download.geofabrik.de/europe/belgium-latest.osm.pbf


if [ "$1" == "--init" ] ; then
# init
echo "init"

# re-download if file is older than 12h or does not exist
if ! test -f $pbffile || [ $pbffile = "`find $pbffile -mmin +720`" ]; then
  curl ${download_sub_path}`date -d "yesterday" '+%y%m%d'`.osm.pbf -o $pbffile
fi

docker exec $(docker ps | grep yosm_postgres | awk '{print $1}') psql -U postgres -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'

# wait for DB to be ready
sleep 2
# time osm2pgsql -U flo -C 1200 --create --database gis $pbffile --style yosm.style
cd osm2pgsql
# export POSTGRES_PASSWORD=`cat ~/.pgpass | cut -d : -f 5`
export PGPASSWORD=`cat ~/.pgpass | cut -d : -f 5`
time osm2pgsql -H 127.0.0.1 -U postgres -C 3000 --slim --create --database gis $pbffile --style yosm.style

else
echo "update"

# get state of update file
# http://download.geofabrik.de/europe/austria-updates/state.txt
# from sequence number -> 2242 -> 000 002 242.osc.gz
sequence_number=`curl "${state_url}" | grep sequenceNumber | cut -d \= -f 2`


# calculate new download path eg:
# http://download.geofabrik.de/europe/austria-updates/000/002/242.osc.gz



fi
