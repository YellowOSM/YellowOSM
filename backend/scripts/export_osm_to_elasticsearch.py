#!/usr/bin/python3
import os
import json
import csv

EXPORT_FILE = "/home/flo/test.export.dump"
EXPORT_ES_FILE = "/home/flo/osm_es_export.json"

# also export polygons
poly = True
poly = False
query_db = True
query_db = False
LIMIT = 100000000000
# LIMIT = 10

# # COMMAND = "sudo -u postgres psql -d gis -c \"SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit};\" | cat >> {file}"
# # COMMAND = "sudo -u postgres psql -d gis -c \"\copy (SELECT P.name,N.lon,N.lat,P.{key} from planet_osm_nodes N, planet_osm_point P WHERE N.id = P.osm_id AND P.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"
# COMMAND = "sudo -u postgres psql -d gis -c \"\copy (SELECT p.name,l.name,lon,lat,p.{key},l.{key} FROM planet_osm_nodes AS n LEFT JOIN planet_osm_point AS p ON n.id = p.osm_id LEFT JOIN planet_osm_polygon AS l ON n.id = l.osm_id WHERE p.{key} = '{value}' OR l.{key} = '{value}' LIMIT {limit}) TO STDOUT With CSV;\" | cat >> {file}"

COMMAND1 = """sudo -u postgres psql -d gis -c \"\copy (
        SELECT p.name,st_x(st_transform(p.way, 4326)),st_y(st_transform(p.way, 4326)),p.{key},
        *
        FROM planet_osm_point AS p
        WHERE p.{key} = '{value}'
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # """
COMMAND2, COMMAND3 = None, None
if poly:
    COMMAND2 = """sudo -u postgres psql -d gis -c \"\copy (
        SELECT p.name,st_x(st_transform(st_centroid(p.way), 4326)),st_y(st_transform(st_centroid(p.way), 4326)),p.{key},
        *
        FROM planet_osm_polygon as p
        WHERE p.{key} = '{value}'
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # """

    # multipolygons
    # mulitpolygons get a negative osm_id in the polygon table!!
    # COMMAND3 = """sudo -u postgres psql -d gis -c \"\copy (
    #     SELECT p.name,st_x(st_transform(st_centroid(p.way), 4326)),st_y(st_transform(st_centroid(p.way), 4326)),p.{key}
    #     FROM planet_osm_polygon as p
    #     LEFT JOIN planet_osm_rels as r ON p.osm_id*-1 = r.id
    #     LEFT JOIN planet_osm_ways as w ON r.parts[1] = w.id
    #     LEFT JOIN planet_osm_nodes as n ON w.nodes[1] = n.id
    #     WHERE ( p.{key} = '{value}' AND p.osm_id < 0 )
    #     LIMIT {limit}
    #     ) TO STDOUT With CSV;\" | cat >> {file}"""
    #     # """

COMMAND4 = """sudo -u postgres psql -d gis -c \"\copy (
        SELECT p.name,st_x(st_transform(p.way, 4326)),st_y(st_transform(p.way, 4326)),p.{key},
        *
        FROM planet_osm_point AS p
        WHERE (p.{key} is not null AND p.{key} != 'vacant')
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # """


# COMMAND4 = """sudo -u postgres psql -d gis -c \"\copy (
#         SELECT p.name,st_x(st_transform(p.way, 4326)),st_y(st_transform(p.way, 4326)),p.{key}
#             FROM planet_osm_nodes AS n
#             LEFT JOIN planet_osm_point AS p ON n.id = p.osm_id
#             WHERE (p.{key} is not null AND p.{key} != 'vacant')
#             LIMIT {limit}
#             ) TO STDOUT With CSV;\" | cat >> {file}"""
#             # """
COMMAND5, COMMAND6 = None, None
if poly:
    COMMAND5 = """sudo -u postgres psql -d gis -c \"\copy (
        SELECT p.name,st_x(st_transform(st_centroid(p.way), 4326)),st_y(st_transform(st_centroid(p.way), 4326)),p.{key},\
        *
        FROM planet_osm_polygon as p
        WHERE (p.{key} is not null AND p.{key} != 'vacant')
        LIMIT {limit}
        ) TO STDOUT With CSV;\" | cat >> {file}"""
        # """
    # COMMAND5 = """sudo -u postgres psql -d gis -c \"\copy (
    #     SELECT p.name,n.lon,n.lat,p.{key}
    #     FROM planet_osm_polygon as p
    #     LEFT JOIN planet_osm_ways as w ON p.osm_id = w.id
    #     LEFT JOIN planet_osm_nodes as n ON n.id = w.nodes[1]
    #     WHERE (p.{key} is not null AND p.{key} != 'vacant')
    #     LIMIT {limit}
    #     ) TO STDOUT With CSV;\" | cat >> {file}"""
    #     # """
    #
    # COMMAND6 = """sudo -u postgres psql -d gis -c \"\copy (
    #     SELECT p.name,n.lon,n.lat,p.{key}
    #     FROM planet_osm_polygon as p
    #     LEFT JOIN planet_osm_rels as r ON p.osm_id*-1 = r.id
    #     LEFT JOIN planet_osm_ways as w ON r.parts[1] = w.id
    #     LEFT JOIN planet_osm_nodes as n ON w.nodes[1] = n.id
    #     WHERE ( p.{key} is not null AND p.{key} != 'vacant' AND p.osm_id < 0 )
    #     LIMIT {limit}
    #     ) TO STDOUT With CSV;\" | cat >> {file}"""
    #     # """

# commands = [COMMAND1, COMMAND2, COMMAND3, COMMAND4, COMMAND5, COMMAND6]
commands = [COMMAND1, COMMAND2, COMMAND4, COMMAND5]

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
export_shop = { "key": "shop",
                    "values":
                       [
                       "supermarket",
                       # Anything goes...
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
any_classes = [export_shop]

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
    # "": ["",],
}


# clear
if query_db:
    open(EXPORT_FILE,'w').close()
    open(EXPORT_ES_FILE,'w').close()


    for cl in classes_to_export:
        for val in cl['values']:
            for command in commands:
                if command and '{value}' in command:
                    command_now = command.format(key=cl['key'], value=val, file=EXPORT_FILE, limit=LIMIT)
                print(command_now)
                os.system(command_now)

    for cl in any_classes:
        for command in commands:
            if command and not '{value}' in command:
                command_now = command.format(key=cl['key'], file=EXPORT_FILE, limit=LIMIT)
            print(command_now)
            os.system(command_now)

    # for cl in classes_to_export:
    #     for val in cl['values']:
    #         command_now = COMMAND1.format(key=cl['key'], value=val, file=EXPORT_FILE, limit=LIMIT )
    #         print(command_now)
    #         os.system(command_now)
    #         if poly:
    #             command_now = COMMAND2.format(key=cl['key'], value=val, file=EXPORT_FILE, limit=LIMIT )
    #             print(command_now)
    #             os.system(command_now)
    #
    # # export any points or polygons that have `key` set
    # for cl in any_classes:
    #     command_now = COMMAND3.format(key=cl['key'], file=EXPORT_FILE, limit=LIMIT )
    #     print(command_now)
    #     os.system(command_now)
    #     if poly:
    #         command_now = COMMAND4.format(key=cl['key'], file=EXPORT_FILE, limit=LIMIT )
    #         print(command_now)
    #         os.system(command_now)









table = """
 osm_id             | bigint               |           |          |
 addr:city          | text                 |           |          |
 addr:street        | text                 |           |          |
 addr:housename     | text                 |           |          |
 addr:housenumber   | text                 |           |          |
 addr:interpolation | text                 |           |          |
 opening_hours      | text                 |           |          |
 website            | text                 |           |          |
 contact:phone      | text                 |           |          |
 contact:email      | text                 |           |          |
 smoking            | text                 |           |          |
 amenity            | text                 |           |          |
 area               | text                 |           |          |
 brand              | text                 |           |          |
 building           | text                 |           |          |
 service            | text                 |           |          |
 name               | text                 |           |          |
 shop               | text                 |           |          |
 sport              | text                 |           |          |
 tourism            | text                 |           |          |
 leisure            | text                 |           |          |
 way                | geometry(Point,3857) |           |          |
"""

# format: name1,lon,lat,type1,*
with open(EXPORT_FILE,'r') as f, open(EXPORT_ES_FILE,'w') as out:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for line in reader:
        if not line:
            continue
        # print(line)
        name = line[0]
        desc = line[3]
        # Stern:
        labels = [
            "addr_city",
            "addr_street",
            "addr_housename",
            "addr_housenumber",
            "addr_interpolation",
            "opening_hours",
            "website",
            "contact_phone",
            "contact_email",
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
            "leisure",
        ]
        label_dict = {label: value for label,value in zip(labels,line[5:]) if value}

        if not name and desc:
            name = amend[desc][0] if desc in amend else desc.capitalize()
        if desc in amend:
            desc += " " + " ".join(amend[desc])
        # FIXXXXME add special case for multipolygons
        if not line[1]:
            continue
        # print(json.dumps({"index": {}}))
        out.write(json.dumps({"index": {}}) + "\n")
        # lat = int(line[2])/10000000
        # lon = int(line[1])/10000000
        lat = float(line[2])
        lon = float(line[1])
        # # print({"name": line[0], "location": [lon,lat], "description": line[3]})
        # print(json.dumps({"name": name, "location": [lon,lat], "description": desc}))
        out.write(json.dumps({"name": name, "location": [lon,lat], "description": desc, "labels": label_dict}) + "\n")
