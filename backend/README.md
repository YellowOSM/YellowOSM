# Backend YellowOSM

## API

Swagger API docs can be found here: https://yellowosm.com/api-docs

The API offers a basic search (in a bounding box, in a city, ...).

It also offers a conversion for Geo58 short strings.

### Routes

the `{variable}` parts of the routes can be set to your requirements of your query.

#### @api.route("/api/")

Just a Hello World.

#### @api.route("/api/osmid/{osm_id}")

get data to a specific `osm_id`, which is the same on Open-Street-Map.

This will get you the data we cache in our data-store. We only store data that relates to businesses.

#### @api.route("/api/osmid/{osm_id}.vcard")

get a vcard download to a specific `osm_id`, which is the same on Open-Street-Map.

This allows you to save contact-data to a business in your mobile-phones address book.

#### @api.route("/api/forward_ip")

forward a client to the YellowOSM Map geo-coordinates matching it's IP (maxmind database).

#### Search

#### @api.route("/api/search/{query}")

issue a basic `query`. This will return all results that match your `query`. 

This can be a lot of data. We limit the results to 10000 entries.

#### @api.route("/api/search/{city}/{query}")

issue a basic `query`. This will return all results that match your `query`. 
the `city` variable allows you to restrict results to a given city, e.g. 'Graz'.

This can be a lot of data. We limit the results to 10000 entries.

#### @api.route("/api/search/{city}/{query}/{limit}")

issue a basic `query`. This will return all results that match your `query`. 
the `city` variable allows you to restrict results to a given city, e.g. 'Graz'.

You can set a maximum results `limit`. We will not return more than `limit` entries.

#### @api.route("/api/search/{top_left_lat}/{top_left_lon}/{bottom_right_lat}/{bottom_right_lon}/{query}")

issue a basic `query`. This will return all results that match your `query`. 

`top_left_lat`, `top_left_lon`, `bottom_right_lat`, `bottom_right_lon` define a bounding box to which the search will be restricted.

This is the kind of search our map uses.

#### Geo58

[Geo58][https://github.com/flowolf/Geo58] is our take on a geo-coordinate short link. We want to link to businesses. 
The resolution we thought to be enough is about 1.1m. Geo58 is available as separate [library from PyPi](https://pypi.org/project/geo58).

The short links are used in our frontend, as a share option.

##### Key Features

* uses base-58 encoding
* can be as short as 8 characters, mostly 9 characters
* maximum length of 10 characters
* resolves to about 1.1m accuracy
* geocoordinates that are close, look similar
* can include a zoom level of a map (20-5)

We implement Geo58 as short link with the yosm.at domain.

#### @api.route("/api/geo58/{zoom}/{x}/{y}")

get a geo58 short-string. `zoom` must be between 5-20. 20 will result in shortest strings. `x` is latitude (float), `y` is longitude (float).

#### @api.route("/api/geo58/{geo58_str}")

get geo-coordinates and zoom from a geo58-short-string.

#### @api.route("/api/redirect_geo58/{geo58_str}")

redirect client to YellowOSM map frontend with the corresponding geo58-short-string geo-coordinates.

## deploy the backend

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

swagger API docs can be found here: https://yellowosm.com/api-docs

## Backend /scripts

The scripts section of the backend is run (mostly) by a cron job to do a daily/nightly run and update
of our data. 

We get the data from [Geofabrik](http://download.geofabrik.de/europe/dach.html), import to a postgres DB 
and finally export data that we want to import into the index (ElasticSearch).

#### csv_labels.py

data structure helper, used for csv export from OSM.

#### export_osm_to_crawler.py

helper script to get data to the crawler.

#### get_city_by_geo-coordinates.py

generates a lookup dict for city names to bounding boxes. Result file can be found in [backend/data](backend/data)

it is supposed to be run manually. city names do not change that often.
this information is used for the API path `api/search/{city}/{query}`.

#### osmosis_pbf_import.sh  

helper script to import OSM data.

#### yosm_poi.py

POI class to import OSM data. Holds data for YellowOSM POIs for export/import. converts and cleans up data if needed.

#### cron_data_downstream.sh  

script to download OSM data. This is run daily on YellowOSM.com.

This script pulls all other scripts together, to build one pipe-line: Geofabrik pbf -> osm2pgsql -> osmosis -> postgresql -> export_osm_to_elasticsearch.py -> tmp_files -> elasticsearch.

#### elasticsearch_data_import.sh  

import data to elasticsearch index.

#### export_osm_to_elasticsearch.py  

convert data to elasticsearch readable format.

queries the postgresql database and dumps all data into a CSV file. then converts it JSON files that are imported to ElasticSearch.
uses yosm_poi.py and cvs_labels.py for data handling.

#### swagger_export.sh

helper script to work around issues with python-responder, which does not serve the API-docs behind a reverse proxy.
only needed for deployment behind a reverse proxy, if API is not on root of the server.

#### osm2pgsql/cron_import_pbf.py  

WIP python version of cron_import_pbf.sh

#### osm2pgsql/cron_import_pbf.sh  

import pbf data into postgresql postgis server.

#### osm2pgsql/osmosis_pbf_import.sh  

prototyping script for data import @ localhost.

#### osm2pgsql/pbf_import.sh

prototyping script for data import @ localhost.

#### osm2pgsql/yosm.style

style file. this basically defines the data we import to postgres. It tells osm2pgsql what keys it should consider.

this is the first step to reduce the amount of data that is in the OSM data. the second step is done by querying the
postgres DB in export_osm_to_elasticsearch.py.