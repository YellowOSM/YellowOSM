#!/bin/bash
WORKOSM_DIR=/home/flo/tmp/osmosis/
pbffile=/tmp/liechtenstein-current.osm.pbf
#sudo mkdir -p $WORKOSM_DIR ; cd $WORKOSM_DIR

cp yosm.style $WORKOSM_DIR/

mkdir -p $WORKOSM_DIR ; cd $WORKOSM_DIR

rm -f configuration.txt
osmosis --read-replication-interval-init workingDirectory=$WORKOSM_DIR
sed -i 's!baseUrl=http://planet.openstreetmap.org/!baseUrl=https://planet.openstreetmap.org/!' configuration.txt
sed -i 's!baseUrl=https://planet.openstreetmap.org/replication/minute!baseUrl=https://download.geofabrik.de/europe/liechtenstein-updates/!' configuration.txt

echo "to init or not to init"
if [ "$1" == "--init" ] ; then
# init
  echo "init"
  sudo -u postgres dropdb gis
  sudo -u postgres createdb gis
  sudo -u postgres psql -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
  sudo -u postgres psql -c "grant all privileges on database gis to flo;"
  sudo -u postgres psql -c "ALTER USER flo WITH PASSWORD 'bla123';"
  export PGPASSWORD=bla123
  sleep 2
  # TODO
  # download
  time nice -10 osm2pgsql --create -U flo -C 1200 --hstore --slim --database gis $pbffile --style yosm.style
  exit
fi

export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres
export PGUSER=flo
export PGPASSWORD=bla123
# export PGPASSWORD=`cat ~/.pgpass|cut -d : -f 5`
cd $WORKOSM_DIR
time nice -10 osmosis --read-replication-interval workingDirectory="${WORKOSM_DIR}" --simplify-change --write-xml-change - | \
osm2pgsql --append -s -C 300 -G --hstore  -r xml --style ${WORKOSM_DIR}/yosm.style -d gis -U $PGUSER -H $PGHOST -
# osm2pgsql --append -s -C 300 -G --hstore -r -d gis -U $PGUSER -H $PGHOST -
# time nice -10 osm2pgsql --append -s -C 300 -G --hstore --style yosm.style --tag-transform-script openstreetmap-carto.lua -d gis -H $PGHOST -U $PGUSER -
