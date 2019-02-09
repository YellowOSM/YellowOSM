#!/bin/bash

# see https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-point.html

# generate test file at https://www.json-generator.com/ with
# [{'repeat(50)': {name: '{{firstName()}} {{surname()}}',address: '{{integer(100, 999)}} {{street()}},{{city()}}, {{state()}}, {{integer(100, 10000)}}',location: "{{floating(47.055593, 47.055593)}},{{floating(15.405622, 15.405622)}}",description: function (tags) {var fruits = ['pharmacy', 'restaurant','bar'];return fruits[tags.integer(0, fruits.length - 1)];}}}]
# and save as graz.json

# BASE_URL='localhost:9200'
BASE_URL='https://es.yosm.at'
INDEX="yosm_dev" # default to dev index
JSONFILE='/tmp/osm_es_export.json'

CURL="curl --interface ens3"
if [[ $1 == '--help' ]]; then
  echo "usage: ${0} --help | [--local] | [yosm|yosm_dev] | [--file es.json]"
  exit
fi
if [[ $1 == '--local' ]]; then
  CURL="curl"
  shift
fi
if [[ $1 == 'yosm' ]]; then
  INDEX=$1
  shift
fi
if [[ $1 == 'yosm_dev' ]]; then
  INDEX=$1
  shift
fi
if [[ $1 == '--file' ]]; then
  JSONFILE=$2
  shift 2
fi

echo "> $CURL \"${BASE_URL}/_cat/indices?v\""
$CURL "${BASE_URL}/_cat/indices?v"

$CURL -XPUT "${BASE_URL}/${INDEX}/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "blocks.read_only": false
  }
}
'

# delete index
$CURL -X DELETE "${BASE_URL}/${INDEX}?pretty"

# create index
# curl -X PUT "${BASE_URL}/${INDEX}?pretty"

# create index and set field mapping
# see https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
$CURL -X PUT "${BASE_URL}/${INDEX}?pretty" -H 'Content-Type: application/json' -d'
{
    "mappings": {
        "_doc": {
            "properties": {
                "location": {
                    "type": "geo_point"
                }
            }
        }
    }
}
'

echo "uploading data to index '$INDEX'..."
# load sample data set
time $CURL -s -H "Content-Type: application/json" -XPOST "${BASE_URL}/${INDEX}/_doc/_bulk?pretty&refresh" --data-binary "@${JSONFILE}" -o /dev/null
echo "done"

# get index status
# $CURL "${BASE_URL}/_cat/indices?v"

# search index
# $CURL "${BASE_URL}/${INDEX}/_search?q=*&pretty"

# search index by geo bounding box
# $CURL "${BASE_URL}/${INDEX}/_search" -H 'Content-Type: application/json' -d'
# {
#   "query": {
#     "geo_bounding_box": {
#       "location": {
#         "top_left": {
#           "lat": 48,
#           "lon": 10
#         },
#         "bottom_right": {
#           "lat": 40,
#           "lon": 16
#         }
#       }
#     }
#   }
# }
# '

# https://grokonez.com/frontend/angular/angular-6/angular-6-elasticsearch-example-quick-start-how-to-add-elasticsearch-js
# CORS für Elasticsearch erlauben


# set read_only


# set index to read-only
$CURL -XPUT "${BASE_URL}/${INDEX}/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "blocks.read_only": true
  }
}
'
