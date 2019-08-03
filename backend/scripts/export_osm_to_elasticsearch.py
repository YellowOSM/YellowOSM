#!/usr/bin/python3
import os
import json
import csv
import argparse

from yosm_poi import YOSM_POI

csv.field_size_limit(100000000)

parser = argparse.ArgumentParser()
parser.add_argument('--local', action="store_true", help="run script in local context without docker postgres")
parser.add_argument('--split', action="store_true", help="split json output file into multiple files; this helps with elasticsearch import")
parser.add_argument('--no-query', action="store_false", help="don't query db, just reformat existing dump.csv")

args = parser.parse_args()
SERVER = not args.local
SPLIT = args.split
query_db = args.no_query

print(args)

# EXPORT_FILE = "/tmp/dump_small.osm"
# EXPORT_ES_FILE = "/tmp/osm_es_export_small.json"

EXPORT_FILE = "/tmp/dump.osm"
EXPORT_ES_FILE = "/tmp/osm_es_export.json"
# if export is split, those are the files with SPLIT_SIZE elements per file...
EXPORT_ES_SPLIT_FILE = "/tmp/osm_es_export_{:03d}.json"
SPLIT_SIZE = 200_000
# SPLIT_SIZE = 400

# also export polygons
poly = True
# poly = False

LIMIT = 100000000000
# LIMIT = 10

if SERVER:
    # `yosm_postgres` is the name of postres' docker image
    query_prefix = "docker exec $(docker ps | grep yosm_postgres | awk '{{print $1}}') psql -U postgres -d gis -c \"\copy ("
else:
    query_prefix = "sudo -u postgres psql -d gis -c \"\copy ("

# # COMMAND = "sudo -u postgres psql -d gis -c \"SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit};\" | cat >> {file}"
# # COMMAND = "sudo -u postgres psql -d gis -c \"\copy (SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"
# COMMAND = "sudo -u postgres psql -d gis -c \"\copy (SELECT p.name,l.name,lon,lat,p.{key},l.{key} FROM planet_osm_nodes AS n LEFT JOIN planet_osm_point AS p ON n.id = p.osm_id LEFT JOIN planet_osm_polygon AS l ON n.id = l.osm_id WHERE p.{key} = '{value}' OR l.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"

COMMAND1 = query_prefix + """
        SELECT p.name,st_x(st_transform(p.way, 4326)),st_y(st_transform(p.way, 4326)),p.{key},'n',
        *
        FROM planet_osm_point AS p
        WHERE p.{key} = '{value}'
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # ) TO STDOUT With CSV;\" | sed 's/$/,C1/g'| cat >> {file}"""
        # """

COMMAND2, COMMAND4 = None, None
if poly:
    COMMAND2 = query_prefix + """
        SELECT p.name,st_x(st_transform(st_centroid(p.way), 4326)),st_y(st_transform(st_centroid(p.way), 4326)),p.{key},'w',
        *
        FROM planet_osm_polygon AS p
        WHERE p.{key} = '{value}'
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # ) TO STDOUT With CSV;\" | sed 's/$/,C2/g'| cat >> {file}"""
        # """

# ANY:
COMMAND3 = query_prefix + """
        SELECT p.name,st_x(st_transform(p.way, 4326)),st_y(st_transform(p.way, 4326)),p.{key},'n',
        *
        FROM planet_osm_point AS p
        WHERE (p.{key} is not null AND p.{key} != 'vacant')
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # ) TO STDOUT With CSV;\" | sed 's/$/,C3/g'| cat >> {file}"""
        # """
if poly:
    COMMAND4 = query_prefix + """
        SELECT p.name,st_x(st_transform(st_centroid(p.way), 4326)),st_y(st_transform(st_centroid(p.way), 4326)),p.{key},'w',\
        *
        FROM planet_osm_polygon AS p
        WHERE (p.{key} is not null AND p.{key} != 'vacant')
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # ) TO STDOUT With CSV;\" | sed 's/$/,C4/g'| cat >> {file}"""
        # """

COMMAND5 = query_prefix + """
        SELECT p.name,st_x(st_transform(p.way, 4326)),st_y(st_transform(p.way, 4326)),p.{key},'n',
        *
        FROM planet_osm_point AS p
        WHERE (p.{key} is not null AND
        ((p.opening_hours is not null OR p.fee = 'yes' OR p.access = 'public' OR
        p.access != 'private')))
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # ) TO STDOUT With CSV;\" | sed 's/$/,C3/g'| cat >> {file}"""
        # """
if poly:
    COMMAND6 = query_prefix + """
        SELECT p.name,st_x(st_transform(st_centroid(p.way), 4326)),st_y(st_transform(st_centroid(p.way), 4326)),p.{key},'w',\
        *
        FROM planet_osm_polygon AS p
        WHERE (p.{key} is not null AND
        ((p.opening_hours is not null OR p.fee = 'yes' OR p.access = 'public' OR
        p.access != 'private')))
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # ) TO STDOUT With CSV;\" | sed 's/$/,C4/g'| cat >> {file}"""
        # """

commands = [COMMAND1, COMMAND2, COMMAND3, COMMAND4, COMMAND5, COMMAND6]

export_amenity = { "key": "amenity",
                    "values" :
                        [
                        "atm",
                        "bar",
                        "bbq",
                        "biergarten",
                        "cafe",
                        "fuel",
                        "drinking_water",
                        "fast_food",
                        "food_court",
                        "ice_cream",
                        "pharmacy",
                        "dentist",
                        "pub",
                        "restaurant",
                        "toilets",
                        "bank",
                        "vending_machine",
                        "doctors",
                        "driving_school",
                        "sports_centre",
                        "arts_centre",
                        "theatre",
                        "marketplace",
                        "brewery",
                        "post_office",
                        "post_box",
                        "telephone",
                        # TODO get new tags from taginfo...
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
export_atm = { "key": "atm",
                    "values":
                       [
                       "yes",
                       ]
                 }
export_shop = { "key": "shop",
                    "values":
                       [
                       "supermarket",
                       # Anything goes...
                       ]
                 }
export_tourism = { "key": "tourism",
                    "values":
                       [
                       "hotel",
                       # Anything goes...
                       # waypoint... guide_post
                       ]
                 }
export_office = { "key": "office",
                    "values":
                       [
                       # Anything goes...
                       # waypoint... guide_post
                       ]
                 }
export_craft = { "key": "craft",
                 "values":
                     ["bakery",
                    "beekeeper",
                    "blacksmith",
                    "bookbinder",
                    "brewery",
                    "carpenter",
                    "caterer",
                    "electrician",
                    "gardener",
                    "key_cutter",
                    "locksmith",
                    "oil_mill",
                    "grinding_mill",
                    "painter",
                    "photographer",
                    "printer",
                    "plumber",
                    "roofer",
                    "sawmill",
                    "shoemaker",
                    "winery",
                    # erweitern auf alle...
                    ]
                }
export_healthcare = { "key": "healthcare",
                        "values": [
                            "pharmacy",
                            "doctor",
                            "alternative",
                            "audiologist",
                            "birthing_center",
                            "blood_donation",
                            "centre",
                            "clinic",
                            "dentist",
                            "dialyst",
                            "hospital",
                            "midwife",
                            "nutrition_counseling",
                            "occupational_therapist",
                            "optometrist",
                            "physiotherapist",
                            "podiatrist",
                            "psychotherapist",
                            "rehabilitation",
                            "speech_therapist",
                            "yes",
                            ]
               }
export_emergency = { "key": "emergency",
                        "values": [
                            "defibrillator",
                            ]
               }
export_place = { "key": "place",
                    "values":
                       [
                       "city",
                       "town",
                       "village",
                       ]
                 }

classes_to_export = [
    export_amenity,
    export_leisure, # leave this in here, even if it's also a special_access_classes element
    export_atm,
    export_healthcare,
    export_place,
    ]
any_classes = [export_shop, export_tourism, export_craft, export_office]
special_access_classes = [export_leisure,]

if query_db:
    # clear files
    open(EXPORT_FILE,'w').close()
    if not SPLIT:
        open(EXPORT_ES_FILE,'w').close()


    for cl in classes_to_export:
        for command in commands[:2]:
            if command and '{value}' in command:
                for val in cl['values']:
                    command_now = command.format(key=cl['key'], value=val, file=EXPORT_FILE, limit=LIMIT)
                    print(command_now)
                    os.system(command_now)

    for cl in any_classes:
        for command in commands[2:4]:
            if command and not '{value}' in command:
                command_now = command.format(key=cl['key'], file=EXPORT_FILE, limit=LIMIT)
                print(command_now)
                os.system(command_now)

    for cl in special_access_classes:
        for command in commands[4:]:
            if command and not '{value}' in command:
                command_now = command.format(key=cl['key'], file=EXPORT_FILE, limit=LIMIT)
                print(command_now)
                os.system(command_now)

############### Export ###################
def read_line_from_csv():
    # format: name1,lon,lat,type1,*
    with open(EXPORT_FILE,'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for line in reader:
            if not line:
                continue
            yield line

def get_filename():
    pass


# elements_in_file = 0
osm_ids = {} # keep track of exported OSM_ids
yosm_type = None
yosm_subtype = None

# if not SPLIT:
#     files = [EXPORT_ES_FILE]
# else:
#     files = [EXPORT_ES_FILE]

def convert_line_to_json(line, osm_ids):
    json_line = None
    if not line[1]:
        return json_line
    # only export osm_id once
    if line[5] in osm_ids:
        return json_line
    else:
        osm_ids[line[5]] = True

    poi = YOSM_POI(line)

    # build elastic search import file:
    json_line = json.dumps({"index": {}}) + "\n"
    lat = poi.lat
    lon = poi.lon

    if poi.yosm_type:
        if poi.yosm_subtype:
            json_line += json.dumps({"name": poi.name, \
                "location": [poi.lon,poi.lat], \
                "type": poi.yosm_type, \
                "subtype": poi.yosm_subtype, \
                "description": poi.desc, "labels": poi.label_dict}) + "\n"
        else:
            json_line += json.dumps({"name": poi.name, \
                "location": [poi.lon,poi.lat], \
                "type": poi.yosm_type, \
                "description": poi.desc, "labels": poi.label_dict}) + "\n"
    else:
        json_line += json.dumps({"name": poi.name, \
            "location": [poi.lon,poi.lat], \
            "description": poi.desc, "labels": poi.label_dict}) + "\n"

    return json_line

def write_elements_to_file(filename, gen, max_elements=SPLIT_SIZE):
    have_elements = False
    with open(filename,'w') as out:
        written_elements = 0
        for line in gen:

            line = convert_line_to_json(line, osm_ids)
            if line == None:
                continue

            out.write(line)

            have_elements = True
            written_elements += 1
            if written_elements >= max_elements:
                return
        else:
            raise StopIteration("done")

print("remove old files:")
rm_files = EXPORT_ES_SPLIT_FILE.format(0).replace('000','???')
os.system('ls ' + rm_files)
os.system('rm ' + rm_files)

print("Export ES json to file(s):")
try:
    file_index = 0
    all_elements = read_line_from_csv()
    while True:
        filename = EXPORT_ES_SPLIT_FILE.format(file_index)
        print(filename)
        write_elements_to_file(filename, all_elements)
        file_index += 1

except StopIteration as ex:
    # print(ex)
    pass
