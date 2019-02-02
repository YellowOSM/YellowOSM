#!/bin/sh

# see https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-point.html

# generate test file at https://www.json-generator.com/ with
# [{'repeat(50)': {name: '{{firstName()}} {{surname()}}',address: '{{integer(100, 999)}} {{street()}},{{city()}}, {{state()}}, {{integer(100, 10000)}}',location: "{{floating(47.055593, 47.055593)}},{{floating(15.405622, 15.405622)}}",description: function (tags) {var fruits = ['pharmacy', 'restaurant','bar'];return fruits[tags.integer(0, fruits.length - 1)];}}}]
# and save as graz.json

# BASE_URL='localhost:9200'
BASE_URL='https://es.yosm.at'
CURL="curl --interface ens3"
if [ $1 = '--local' ]; then
  CURL="curl"
fi
JSONFILE='osm_es_export.json'

$CURL -XPUT "{$BASE_URL}/yosm/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "blocks.read_only": false
  }
}
'

# delete yosm index
$CURL -X DELETE "{$BASE_URL}/yosm?pretty"

# create yosm index
# curl -X PUT "localhost:9200/yosm?pretty"

# create index and set field mapping
# see https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
$CURL -X PUT "{$BASE_URL}/yosm?pretty" -H 'Content-Type: application/json' -d'
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

# load sample data set
$CURL -H "Content-Type: application/json" -XPOST "{$BASE_URL}/yosm/_doc/_bulk?pretty&refresh" --data-binary "@${JSONFILE}"

# get index status
# $CURL "{$BASE_URL}/_cat/indices?v"

# search index
# $CURL "{$BASE_URL}/yosm/_search?q=*&pretty"

# search index by geo bounding box
# $CURL "{$BASE_URL}/yosm/_search" -H 'Content-Type: application/json' -d'
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

$CURL -XPUT "{$BASE_URL}/yosm/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "blocks.read_only": true
  }
}
'
