#!/usr/bin/python3
import argparse
import logging
import os
import time
import datetime
import sys

# TODO add ability to add more regions
# REGIONS=["liechtenstein"]

# REGION="austria"
# REGION="germany"
# REGION="dach" # Germany, Austria, Switzerland
# REGION="luxembourg"
REGION="liechtenstein"
# TODO
# add continent (eg. EUROPE etc), for path

# pbffile="/tmp/dach-current.osm.pbf"
# state_url="http://download.geofabrik.de/europe/dach-updates/state.txt"
# download_sub_path="https://download.geofabrik.de/europe/dach-"

# austria
# pbffile="/tmp/austria-current.osm.pbf"
# state_url="http://download.geofabrik.de/europe/austria-updates/state.txt"
# download_sub_path="https://download.geofabrik.de/europe/austria-"

WORKOSM_DIR="/home/flo/tmp/osmosis/"

# testing small file:
pbffile="/tmp/"+REGION+"-current.osm.pbf"
statefile="/tmp/"+REGION+"-state.txt"
state_url="http://download.geofabrik.de/europe/"+REGION+"-updates/state.txt"
download_sub_path="https://download.geofabrik.de/europe/"+REGION+"-"
pbf_path="http://download.geofabrik.de/europe/"+REGION+"-latest.osm.pbf"
# curl http://download.geofabrik.de/europe/liechtenstein-latest.osm.pbf -O $WORKOSM_DIR/liechtenstein-latest.osm.pbf
# wget "https://download.geofabrik.de/europe/liechtenstein-updates/state.txt" -O $WORKOSM_DIR/state.txt


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
parser.add_argument('--update-db', action="store_true",
                     help='update existing database with osc files from remote server')
parser.set_defaults(update_db=False)


args = vars(parser.parse_args())

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(10)
# logger.setLevel(50)

logger.debug(args)

def prepare_osmosis():
    WORKDIR="/home/flo/tmp/osmosis/"
    # mkdir -p $WORKOSM_DIR ; cd $WORKOSM_DIR


def init():
    logger.debug("initializing DB")

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

def download_pbf(force_download=False):
    # re-download if file is older than 12h or does not exist
    # if ! test -f $pbffile || [ $pbffile = "`find $pbffile -mmin +720`" ]; then
    #   curl ${download_sub_path}`date -d "yesterday" '+%y%m%d'`.osm.pbf -o $pbffile
    # fi

    # yesterday=(datetime.date.today()-datetime.timedelta(1)).strftime("%y%m%d")
    # # download
    # download_url = download_sub_path+"{}.osm.pbf".format(yesterday)
    download_url = download_sub_path+"latest.osm.pbf"
    logger.debug("would be downloading: {} to {}".format(download_url, pbffile))

    # download only if older than 12h
    do_download = False
    try:
        now = datetime.datetime.now()
        logger.debug("now: " + str(now))
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(pbffile))
        logger.debug("file mtime: " + str(mtime))
        # print(mtime)
        age = (now - mtime).total_seconds()
        if age > 3600*12 or force_download: # older than 12 hours
            do_download = True
    except FileNotFoundError as e:
        age = None
        mtime = None
        do_download = True # force download if file does not exist
        pass

    logger.debug(str(mtime) + " " + str(now) + " age: " + str(age))
    # TODO remove next line
    # do_download = False
    if do_download:
        logger.debug("downloading: {} to {}".format(download_url, pbffile))
        os.system("curl {} -o {}".format(download_url, pbffile))
        os.system("curl {} -o {}".format(state_url, ))
    else:
        logger.debug("NOT downloading")


def update_db():
    # echo "update"
    logger.debug("updating DB...")

    # get state of update file
    # http://download.geofabrik.de/europe/austria-updates/state.txt
    # from sequence number -> 2242 -> 000 002 242.osc.gz
    #sequence_number=`curl "${state_url}" | grep sequenceNumber | cut -d \= -f 2`


    # calculate new download path eg:
    # http://download.geofabrik.de/europe/austria-updates/000/002/242.osc.gz

def main(args):
    INIT = args['init']
    FORCE_DOWNLOAD = args['force_download']
    UPDATE_DB = args['update_db']

    # no params given -> exit
    if not INIT and not FORCE_DOWNLOAD and not UPDATE_DB:
        parser.print_help()
        return

    if FORCE_DOWNLOAD:
        download_pbf(force_download=FORCE_DOWNLOAD)

    if UPDATE_DB:
        # don't init DB if update-db is chosen
        INIT = False
        update_db()

    if INIT:
        init()

if __name__ == '__main__':
    main(args)
