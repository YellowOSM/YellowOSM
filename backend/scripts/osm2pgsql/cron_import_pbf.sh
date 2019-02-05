#!/bin/sh

pbffile="/tmp/austria-current.osm.pbf"

# TODO tolerate missing $pbffile

# don't re-download before 12h after last download
if [ $pbffile = "`find $pbffile -mmin +720`" ]; then
  curl https://download.geofabrik.de/europe/austria-`date -d "yesterday" '+%y%m%d'`.osm.pbf -o $pbffile
fi
docker exec $(docker ps | grep yosm_postgres | awk '{print $1}') psql -U postgres -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
sleep 2
# time osm2pgsql -U flo -C 1200 --create --database gis $pbffile --style yosm.style
cd osm2pgsql
# export POSTGRES_PASSWORD=`cat ~/.pgpass | cut -d : -f 5`
export PGPASSWORD=`cat ~/.pgpass | cut -d : -f 5`
time osm2pgsql -H 127.0.0.1 -U postgres -C 3000 --slim --create --database gis $pbffile --style yosm.style
