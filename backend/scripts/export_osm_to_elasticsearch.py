#!/usr/bin/python3
import os
import json
import csv

EXPORT_FILE = "/home/flo/test.export.dump"
EXPORT_ES_FILE = "/home/flo/osm_es_export.json"

# also export polygons
poly = True

# LIMIT = 10
LIMIT = 100000000000
# # COMMAND = "sudo -u postgres psql -d gis -c \"SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit};\" | cat >> {file}"
# # COMMAND = "sudo -u postgres psql -d gis -c \"\copy (SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"
# COMMAND = "sudo -u postgres psql -d gis -c \"\copy (SELECT p.name,l.name,lon,lat,p.{key},l.{key} FROM planet_osm_nodes AS n LEFT JOIN planet_osm_point AS p ON n.id = p.osm_id LEFT JOIN planet_osm_polygon AS l ON n.id = l.osm_id WHERE p.{key} = '{value}' OR l.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"

COMMAND1 =     "sudo -u postgres psql -d gis -c \"\copy (SELECT p.name,lon,lat,p.{key} FROM planet_osm_nodes AS n LEFT JOIN planet_osm_point AS p ON n.id = p.osm_id WHERE p.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"
if poly:
    COMMAND2 = "sudo -u postgres psql -d gis -c \"\copy (SELECT p.name,n.lon,n.lat,p.{key} FROM planet_osm_polygon as p LEFT JOIN planet_osm_ways as w ON p.osm_id = w.id LEFT JOIN planet_osm_nodes as n ON n.id = w.nodes[1] WHERE p.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"

export_amenity = { "key": "amenity",
                    "values" :
                        [
                        "bar",
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
                       [
                       "hackerspace",
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
    # export_leisure,
    # export_craft,
    ]

# clear
open(EXPORT_FILE,'w').close()
open(EXPORT_ES_FILE,'w').close()

for cl in classes_to_export:
    for val in cl['values']:


        command_now = COMMAND1.format(key=cl['key'], value=val, file=EXPORT_FILE, limit=LIMIT )
        print(command_now)
        os.system(command_now)
        if poly:
            command_now = COMMAND2.format(key=cl['key'], value=val, file=EXPORT_FILE, limit=LIMIT )
            print(command_now)
            os.system(command_now)

# # format: name1,name2,lon,lat,type1,type2
# format: name1,lon,lat,type1
with open(EXPORT_FILE,'r') as f, open(EXPORT_ES_FILE,'w') as out:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for line in reader:
        if not line:
            continue
        print(line)
        # name = line[0] if line[0] else line[1]
        # desc = line[4] if line[4] else line[5]+"_poly"
        name = line[0]
        desc = line[3]
        # FIXXXXME add special case for multipolygons
        if not line[1]:
            continue
        # print(json.dumps({"index": {}}))
        out.write(json.dumps({"index": {}}) + "\n")
        lat = int(line[2])/10000000
        lon = int(line[1])/10000000
        # # print({"name": line[0], "location": [lon,lat], "description": line[3]})
        # print(json.dumps({"name": name, "location": [lon,lat], "description": desc}))
        out.write(json.dumps({"name": name, "location": [lon,lat], "description": desc}) + "\n")
