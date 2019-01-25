#!/usr/bin/python3
import os
import json
import csv

EXPORT_FILE = "/home/flo/test.export.dump"
EXPORT_ES_FILE = "/home/flo/test.export.es.json"

LIMIT = 100000000000
# COMMAND = "sudo -u postgres psql -d gis -c \"SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit};\" | cat >> {file}"
COMMAND = "sudo -u postgres psql -d gis -c \"\copy (SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"

export_amenity = { "key": "amenity",
                    "values" :
                        ["bar",
                        "bbq",
                        "biergarten",
                        "cafe",
                        "drinking_water",
                        "fast_food",
                        "food_court",
                        "ice_cream",
                        "pharmacy",
                        "pub",
                        "restaurant",
                        "toilets",
                        ]
                 }
export_leisure = { "key": "leisure",
                    "values":
                       ["hackerspace",
                       "bowling_alley",
                       "fishing",
                       "fitness_centre",
                       "marina",
                       "park",
                       "playground",
                       ]
                 }
# FIXXXXME see how those can be exported
# export_craft = { "key": "craft",
#                  "values":
#                      ["bakery",
#                     "beekeeper",
#                     "blacksmith",
#                     "bookbinder",
#                     "brewery",
#                     "carpenter",
#                     "caterer",
#                     "electrician",
#                     "gardener",
#                     "key_cutter",
#                     "locksmith",
#                     "oil_mill",
#                     "painter",
#                     "photographer",
#                     "plumber",
#                     "roofer",
#                     "sawmill",
#                     "shoemaker",
#                     "winery",
#                     ]
#                 }
classes_to_export = [
    export_amenity,
    export_leisure,
    # export_craft,
    ]

for cl in classes_to_export:
    for val in cl['values']:
        command_now = COMMAND.format(key=cl['key'], value=val, file=EXPORT_FILE, limit=LIMIT )
        print(command_now)
        os.system(command_now)
        #exit()

# format: name,lon,lat,type
with open(EXPORT_FILE,'r') as f, open(EXPORT_ES_FILE,'w') as out:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for line in reader:
        if not line:
            continue
        # print(line)
        print(json.dumps({"index": {}}))
        out.write(json.dumps({"index": {}}) + "\n")
        lat = int(line[2])/10000000
        lon = int(line[1])/10000000
        # print({"name": line[0], "location": [lon,lat], "description": line[3]})
        print(json.dumps({"name": line[0], "location": [lon,lat], "description": line[3]}))
        out.write(json.dumps({"name": line[0], "location": [lon,lat], "description": line[3]}) + "\n")
