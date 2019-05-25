#!/usr/bin/python3
import argparse
import logging
import os
import time
import datetime
import sys


# pbffile="/tmp/dach-current.osm.pbf"
# state_url="http://download.geofabrik.de/europe/dach-updates/state.txt"
# download_sub_path="https://download.geofabrik.de/europe/dach-"

pbffile="/tmp/austria-current.osm.pbf"
state_url="http://download.geofabrik.de/europe/austria-updates/state.txt"
download_sub_path="https://download.geofabrik.de/europe/austria-"
# testing small file:
pbffile="/tmp/liechtenstein-current.osm.pbf"
state_url="http://download.geofabrik.de/europe/liechtenstein-updates/state.txt"
download_sub_path="https://download.geofabrik.de/europe/liechtenstein-"
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
parser.add_argument('--force-download', action="store_true",
                     help='force download of pbf file, even if not older than 12 hours')
parser.set_defaults(force_download=False)

args = vars(parser.parse_args())
INIT = args['init']
FORCE_DOWNLOAD = args['force_download']

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(10)
# print(args)
# print(INIT)

logger.debug(args)

if INIT:
    logger.debug("init")

    # re-download if file is older than 12h or does not exist
    # if ! test -f $pbffile || [ $pbffile = "`find $pbffile -mmin +720`" ]; then
    #   curl ${download_sub_path}`date -d "yesterday" '+%y%m%d'`.osm.pbf -o $pbffile
    # fi

    yesterday=(datetime.date.today()-datetime.timedelta(1)).strftime("%y%m%d")
    # download
    download_url = download_sub_path+"{}.osm.pbf".format(yesterday)

    logger.debug("would be downloading: {} to {}".format(download_url, pbffile))

    # download only if older than 12h
    do_download = False
    try:
        now = datetime.datetime.now()
        print(now)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(pbffile))
        print(mtime)
        age = (now - mtime).total_seconds()
        if age > 3600*12 or FORCE_DOWNLOAD: # older than 12 hours
            do_download = True
    except FileNotFoundError as e:
        age = None
        mtime = None
        do_download = True # force download if file does not exist
        pass

    logger.debug(str(mtime) + " " + str(now) + " age: " + str(age))
    if do_download:
        logger.debug("downloading: {} to {}".format(download_url, pbffile))
    do_download = False
    if do_download:
        os.system("curl {} -o {}".format(download_url, pbffile))

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
