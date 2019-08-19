#!/bin/bash

# pbffile="/tmp/austria-current.osm.pbf"
WORKOSM_DIR="/root/osmosis_workdir/"

export PGHOST=127.0.0.1
export PGPORT=5432
export PGUSER=postgres
# export PGPASSWORD=postgres_007%
export PGPASSWORD=`cat ~/.pgpass | cut -d : -f 5`

RAM_CACHE=5000

region="liechtenstein"
region="austria"
region="dach"
# pbffile="/tmp/liechtenstein-current.osm.pbf"
#pbffile="/tmp/austria-current.osm.pbf"
pbffile="/tmp/${region}-current.osm.pbf"
PBF_FILE=$pbffile
statefile="/tmp/state.txt"
# state_url="http://download.geofabrik.de/europe/liechtenstein-updates/state.txt"
# state_url="http://download.geofabrik.de/europe/austria-updates/state.txt"
state_url="http://download.geofabrik.de/europe/${region}-updates/state.txt"
## download_sub_path="https://download.geofabrik.de/europe/austria-"
# download_path="https://download.geofabrik.de/europe/liechtenstein-latest.osm.pbf"
# download_path="https://download.geofabrik.de/europe/austria-latest.osm.pbf"
download_path="https://download.geofabrik.de/europe/${region}-latest.osm.pbf"
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
mkdir -p $WORKOSM_DIR
# re-download if file is older than 12h or does not exist
if ! test -f $pbffile || [ $pbffile = "`find $pbffile -mmin +720`" ]; then
  # curl ${download_sub_path}`date -d "yesterday" '+%y%m%d'`.osm.pbf -o $pbffile
  curl ${download_path} -o $pbffile
  # state file generated below:
  # curl ${state_url} -o $statefile
fi

docker exec $(docker ps | grep yosm_postgres | awk '{print $1}') psql -U postgres -d gis -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'

# wait for DB to be ready
sleep 2
# time osm2pgsql -U flo -C 1200 --create --database gis $pbffile --style yosm.style
## cd osm2pgsql
# export POSTGRES_PASSWORD=`cat ~/.pgpass | cut -d : -f 5`
export PGPASSWORD=`cat ~/.pgpass | cut -d : -f 5`
time osm2pgsql -H $PGHOST -U $PGUSER -C $RAM_CACHE --slim --create --number-processes 8 --database gis $pbffile --style yosm.style

# PBF_FILE=liechtenstein-latest.osm.pbf
REPLICATION_BASE_URL="$(osmium fileinfo -g 'header.option.osmosis_replication_base_url' "${PBF_FILE}")"
echo -e "baseUrl=${REPLICATION_BASE_URL}\nmaxInterval=90000" > "${WORKOSM_DIR}/configuration.txt"

REPLICATION_SEQUENCE_NUMBER="$( printf "%09d" "$(osmium fileinfo -g 'header.option.osmosis_replication_sequence_number' "${PBF_FILE}")" | sed ':a;s@\B[0-9]\{3\}\>@/&@;ta' )"
curl -s -L -o "${WORKOSM_DIR}/state.txt" "${REPLICATION_BASE_URL}/${REPLICATION_SEQUENCE_NUMBER}.state.txt"

else
  echo "update"
  mkdir -p $WORKOSM_DIR
  cp yosm.style $WORKOSM_DIR/
  # WORKOSM_DIR=/home/tileserver/osmosisworkingdir
  # cd ~/src/openstreetmap-carto
  # HOSTNAME=localhost # set it to the actual ip address or host name
  osmosis --read-replication-interval workingDirectory=${WORKOSM_DIR} --simplify-change --write-xml-change - | \
  osm2pgsql --append -s -C $RAM_CACHE -G --number-processes 8 --style ${WORKOSM_DIR}/yosm.style -r xml -d gis -H $PGHOST -U $PGUSER -
  # osm2pgsql --append -s -C 300 -G --hstore --style yosm.style -r xml -d gis -H $PGHOST -U $PGUSER -

fi
