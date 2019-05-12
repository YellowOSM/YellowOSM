#!/bin/bash

# pbffile="/home/flo/Downloads/Graz.osm.pbf"

#pbffile="/home/flo/Downloads/austria-latest.osm.pbf"
pbffile="/tmp/austria-190508.osm.pbf"
oscfile="/tmp/242.osc"

if [ "$1" == "--init" ] ; then
# init
echo "init"
sudo -u postgres dropdb gis
sudo -u postgres createdb gis
sudo -u postgres psql -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
sudo -u postgres psql -c "grant all privileges on database gis to flo;"
sleep 5
time nice -10 osm2pgsql --create -U flo -C 1200 --slim --database gis $pbffile --style yosm.style
# time nice -10 osm2pgsql -U flo -C 1000 --create --database gis $pbffile --style yosm.style
# time nice -10 osm2pgsql -U flo -C 1200 --slim --create --database gis $pbffile --style yosm.style


else
# update
echo "update"
gunzip ${oscfile}.gz 2> /dev/null
time nice -10 osm2pgsql --append -U flo -C 1200 --number-processes 3 --slim --database gis $oscfile --style yosm.style
fi
