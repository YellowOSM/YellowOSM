# Backend YellowOSM

## API

swagger API docs can be found here: https://yellowosm.com/api-docs

The API offers a basic search (in a bounding box, in a city, ...).

It also offers a conversion for Geo58 short strings.



### install and run
```bash
pipenv --python 3.7
```
run:
```bash
pipenv run python api.py
# or
pipenv shell
python api.py
deactivate
```

## Docs

The Backend uses the GeoLite2-City database from maxmind to resolve Client IP addresses and locate the user (to show the most probale relevant map).


## api.py

the main API, implemented with python-responder.

## Backend /scripts

### csv_labels.py

data structure helper, used for csv export from OSM.

### export_osm_to_crawler.py

helper script to get data to the crawler.

### get_city_by_geo-coordinates.py

generates a lookup dict for city names to bounding boxes. Result file can be found in [backend/data](backend/data)

### osmosis_pbf_import.sh  

helper script to import OSM data.

### yosm_poi.py

POI class to import OSM data. Holds data for YellowOSM POIs for export/import.

### cron_data_downstream.sh  

script to download OSM data. This is run daily on YellowOSM.com.

This script pulls all other scripts together, to build one pipe-line: Geofabrik pbf -> osm2pgsql -> osmosis -> export_osm_to_elasticsearch.py -> tmp_files -> elasticsearch

### elasticsearch_data_import.sh  

import data to elasticsearch index.

### export_osm_to_elasticsearch.py  

convert data to elasticsearch readable format.

### osm2pgsql/cron_import_pbf.py  

WIP python version of cron_import_pbf.sh

### osm2pgsql/cron_import_pbf.sh  

import pbf into postgresql postgis server

### osm2pgsql/osmosis_pbf_import.sh  

prototyping script for data import @ localhost.

### osm2pgsql/pbf_import.sh

prototyping script for data import @ localhost.

### osm2pgsql/yosm.style

style file. this basically reduces the data we import to postgres. It tells osm2pgsql what keys it should consider.
