#!/usr/bin/python3
import argparse
import logging
import os
import time
import datetime
import sys

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


parser = argparse.ArgumentParser(description='import or update osm data from geofabrik')
parser.add_argument('--init', action="store_true",
                     help='initialize DB (deletes all old content)')
parser.set_defaults(init=False)

args = vars(parser.parse_args())
INIT = args['init']

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(10)
# print(args)
# print(INIT)

if INIT:
    logger.debug("init")

    # re-download if file is older than 12h or does not exist
    # if ! test -f $pbffile || [ $pbffile = "`find $pbffile -mmin +720`" ]; then
    #   curl ${download_sub_path}`date -d "yesterday" '+%y%m%d'`.osm.pbf -o $pbffile
    # fi

    yesterday=(datetime.date.today()-datetime.timedelta(1)).strftime("%y%m%d")
    # download
    download_url = download_sub_path+"{}.osm.pbf".format(yesterday)

    logger.debug("downloading: {} to {}".format(download_url, pbffile))

    # download only if older than 12h
    try:
        now = datetime.datetime.now()
        mtime = os.path.getmtime(pbffile)
    except FileNotFoundError as e:
        age = None
        pass

    logger.debug(mtime, now)

    # os.system("curl {} -o {}".format(download_url, pbffile))

    # command = "docker exec $(docker ps | grep yosm_postgres | " +
    #           "awk '{print $1}') psql -U postgres -d gis " +
    #           "-c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'"
    command = "touch success_bla_bla.txt"
    os.system(command)

    # wait for DB to be ready
    # sleep 2
    time.sleep(2)

    # time osm2pgsql -U flo -C 1200 --create --database gis $pbffile --style yosm.style
    # cd osm2pgsql
    # export POSTGRES_PASSWORD=`cat ~/.pgpass | cut -d : -f 5`
    PGPASS=""
    with open("/home/flo/.pgpass") as f:
        # export PGPASSWORD=`cat ~/.pgpass | cut -d : -f 5`
        PGPASS=f.read().split(":")[4].strip()

    os.environ["PGPASSWORD"] = PGPASS
    # os.system("cd osm2pgsql; time osm2pgsql -H 127.0.0.1 -U postgres -C 3000 --slim --create --database gis {} --style yosm.style".format(pbffile))
    os.system("echo 'it works!'; echo $PGPASSWORD")

else:
    # echo "update"
    logger.debug("update")

    # get state of update file
    # http://download.geofabrik.de/europe/austria-updates/state.txt
    # from sequence number -> 2242 -> 000 002 242.osc.gz
    #sequence_number=`curl "${state_url}" | grep sequenceNumber | cut -d \= -f 2`


    # calculate new download path eg:
    # http://download.geofabrik.de/europe/austria-updates/000/002/242.osc.gz
