#!/usr/bin/python3
import os
import json
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--local',action="store_true", help="run script in local context without docker postgres")

args = vars(parser.parse_args())
SERVER = not args['local']

EXPORT_FILE = "dump.osm"
EXPORT_ES_FILE = "osm_es_export.json"

# also export polygons
poly = True
# poly = False
query_db = True
query_db = False
LIMIT = 100000000000
# LIMIT = 10

if SERVER:
    # `yosm_postgres` is the name of postres' docker image
    query_prefix = "docker exec $(docker ps | grep yosm_postgres | awk '{{print $1}}')  psql -U postgres -d gis -c \"\copy ("
else:
    query_prefix = "sudo -u postgres psql -d gis -c \"\copy ("

# # COMMAND = "sudo -u postgres psql -d gis -c \"SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit};\" | cat >> {file}"
# # COMMAND = "sudo -u postgres psql -d gis -c \"\copy (SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"
# COMMAND = "sudo -u postgres psql -d gis -c \"\copy (SELECT p.name,l.name,lon,lat,p.{key},l.{key} FROM planet_osm_nodes AS n LEFT JOIN planet_osm_point AS p ON n.id = p.osm_id LEFT JOIN planet_osm_polygon AS l ON n.id = l.osm_id WHERE p.{key} = '{value}' OR l.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"

COMMAND1 = query_prefix + """
        SELECT p.name,st_x(st_transform(p.way, 4326)),st_y(st_transform(p.way, 4326)),p.{key},
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
        SELECT p.name,st_x(st_transform(st_centroid(p.way), 4326)),st_y(st_transform(st_centroid(p.way), 4326)),p.{key},
        *
        FROM planet_osm_polygon AS p
        WHERE p.{key} = '{value}'
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # ) TO STDOUT With CSV;\" | sed 's/$/,C2/g'| cat >> {file}"""
        # """

# ANY:
COMMAND3 = query_prefix + """
        SELECT p.name,st_x(st_transform(p.way, 4326)),st_y(st_transform(p.way, 4326)),p.{key},
        *
        FROM planet_osm_point AS p
        WHERE (p.{key} is not null AND p.{key} != 'vacant')
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # ) TO STDOUT With CSV;\" | sed 's/$/,C3/g'| cat >> {file}"""
        # """
if poly:
    COMMAND4 = query_prefix + """
        SELECT p.name,st_x(st_transform(st_centroid(p.way), 4326)),st_y(st_transform(st_centroid(p.way), 4326)),p.{key},\
        *
        FROM planet_osm_polygon AS p
        WHERE (p.{key} is not null AND p.{key} != 'vacant')
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # ) TO STDOUT With CSV;\" | sed 's/$/,C4/g'| cat >> {file}"""
        # """

commands = [COMMAND1, COMMAND2, COMMAND3, COMMAND4]

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
                        "pub",
                        "restaurant",
                        "toilets",
                        "bank",
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
                    ]
                }
classes_to_export = [
    export_amenity,
    export_leisure,
    export_craft,
    export_atm,
    ]
any_classes = [export_shop, export_tourism,]

# additional info:
# first element will be alternative name!!
amend = {
    "atm": ["Bankomat", "Geldautomat"],
    "restaurant": ["Gasthaus", "Wirtshaus"],
    "pub": ["Gasthaus", "Wirtshaus"],
    "bar": ["Bar","Beisl"],
    "fuel": ["Tankstelle"],
    "toilets": ["Toilette","Klo","Häuschen"],
    "pharmacy": ["Apotheke","Arzneimittel","Medikamente"],
    "car_repair": ["Werkstatt"],
    "kiosk": ["Trafik",],
    "tobacco": ["Trafik",],
    "florist": ["Blumen",],
    "laundry": ["Putzerei", "Wäscherei"],
    "mall": ["Einkaufszentrum",],
    "department_store": ["Kaufhaus",],
    "jewelry": ["Juwelier","Schmuck"],
    "hairdresser": ["Friseur","Frisör",],
    "doityourself": ["Baumarkt"],
    "supermarket": ["Supermarkt"],
    "playground": ["Spielplatz",],
    "drinking_water": ["Trinkasser","Wasser",],
    "fast_food": ["Fast Food","Imbiss",],
    "bakery": ["Bäckerei","Bäcker","Brot",],
    "optician": ["Optiker","Brillen"],
    "perfumery": ["Parfümerie",],
    "fabric": ["Stoffe",],
    "luggage": ["Koffer","Gepäck","Taschen",],
    "photo": ["Fotograf","Photograph","Fotograph","Photograf",],
    "clothes": ["Kleidung","Bekleidung","Gewand","Gwand","Hemden",],
    "ice_cream": ["Speiseeis","Eis","Eiscreme",],
    "beekeeper": ["Imker"],
    "blacksmith": ["Schmied"],
    "bookbinder": ["Buchbinder"],
    "brewery": ["Brauerei"],
    "carpenter": ["Tischler"],
    "caterer": ["Caterer"],
    "electrician": ["Elektriker"],
    "gardener": ["Gärtner"],
    "key_cutter": ["Schlüsseldienst"],
    "locksmith": ["Schlüsseldienst","Aufsperrdienst"],
    "oil_mill": ["Öl-Mühle", "Ölpresse"],
    "painter": ["Maler"],
    "photographer": ["Fotograf","Photograph","Fotograph","Photograf",],
    "printer": ["Druckerei"],
    "plumber": ["Installateur", "Klempner"],
    "roofer": ["Dachdecker"],
    "sawmill": ["Sägewerk"],
    "shoemaker": ["Schuster"],
    "winery": ["Weinkellerei", "Weingut", "Kellerei"],
    # "": ["",],
}


# clear
if query_db:
    open(EXPORT_FILE,'w').close()
    open(EXPORT_ES_FILE,'w').close()


    for cl in classes_to_export:
        for command in commands[:2]:
            if command and '{value}' in command:
                for val in cl['values']:
                    command_now = command.format(key=cl['key'], value=val, file=EXPORT_FILE, limit=LIMIT)
                    print(command_now)
                    os.system(command_now)

    for cl in any_classes:
        for command in commands[2:]:
            if command and not '{value}' in command:
                command_now = command.format(key=cl['key'], file=EXPORT_FILE, limit=LIMIT)
                print(command_now)
                os.system(command_now)

table = """sudo -u postgres psql  -d gis -c "\d planet_osm_point" | \
grep -A 500 osm_id | grep -B 500 \ way\   | grep -v way |\
 cut -d \| -f 1 | sed 's/ //g' | sed 's/^/"/g;s/$/", /;s/:/_/g'
"""

labels = [
    "osm_id",
    "addr_city",
    "addr_street",
    "addr_place",
    "addr_housename",
    "addr_housenumber",
    "addr_postcode",
    "addr_interpolation",
    "opening_hours",
    "website",
    "contact_website",
    "contact_twitter",
    "contact_whatsapp",
    "contact_facebook",
    "contact_telegram",
    "contact_foursquare",
    "contact_youtube",
    "contact_linkedin",
    "contact_xing",
    "contact_vhf",
    "contact_instagram",
    "contact_diaspora",
    "contact_skype",
    "contact_viber",
    "contact_mastodon",
    "contact_xmpp",
    "contact_fax",
    "contact_phone",
    "contact_mobile",
    "phone",
    "leisure",
    "contact_email",
    "email",
    "smoking",
    "amenity",
    "area",
    "brand",
    "building",
    "service",
    "name",
    "shop",
    "sport",
    "tourism",
    "craft",
    "atm",
]

print("Export ES json:")
# format: name1,lon,lat,type1,*
with open(EXPORT_FILE,'r') as f, open(EXPORT_ES_FILE,'w') as out:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    osm_ids = {}
    for line in reader:
        if not line:
            continue

        # only export osm_id once
        if line[4] in osm_ids:
            continue
        else:
            osm_ids[line[4]] = True

        name = line[0]
        desc = line[3]
        label_dict = {label: value for label,value in zip(labels,line[4:]) if value}

        if 'atm' in label_dict and label_dict['atm'] == 'no':
            del label_dict['atm']

        if not name and desc:
            name = amend[desc][0] if desc in amend else desc.capitalize()
        # if desc in amend:
        #     desc += " " + " ".join(amend[desc])
        for typus in ['amenity','leisure','shop', 'craft', 'tourism']:
            if typus in label_dict and label_dict[typus] in amend:
                desc += " " + " ".join(amend[label_dict[typus]])
        if 'atm' in label_dict and label_dict['atm'] != 'no':
            desc += " " + " ".join(amend['atm'])

        if not line[1]:
            continue
        out.write(json.dumps({"index": {}}) + "\n")
        lat = float(line[2])
        lon = float(line[1])
        # # print({"name": line[0], "location": [lon,lat], "description": line[3]})
        # print(json.dumps({"name": name, "location": [lon,lat], "description": desc}))
        out.write(json.dumps({"name": name, "location": [lon,lat], "description": desc, "labels": label_dict}) + "\n")
