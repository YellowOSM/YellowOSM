#!/bin/sh

# pbffile="/home/flo/Downloads/Graz.osm.pbf"
pbffile="/home/flo/Downloads/austria-latest.osm.pbf"
# sudo -u postgres dropdb gis
# sudo -u postgres createdb gis
# sudo -u postgres psql -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
# sudo -u postgres psql -c "grant all privileges on database gis to flo;"
time osm2pgsql -U flo -C 600 --create --database gis $pbffile --style yosm.style
