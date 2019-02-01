#!/bin/sh

dropdb gis
createdb gis
psql -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
osm2pgsql --create --database gis Graz.osm.pbf --style yosm.style