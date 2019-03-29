#!/usr/bin/python3
import os
import json
import csv
import argparse

csv.field_size_limit(100000000)

parser = argparse.ArgumentParser()
parser.add_argument('--local',action="store_true", help="run script in local context without docker postgres")

args = vars(parser.parse_args())
SERVER = not args['local']

# EXPORT_FILE = "/tmp/dump_small.osm"
# EXPORT_ES_FILE = "/tmp/osm_es_export_small.json"

EXPORT_FILE = "/tmp/dump.osm"
EXPORT_ES_FILE = "/tmp/osm_es_export.json"

# also export polygons
poly = True
# poly = False
query_db = True
# query_db = False
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
                        "post_office",
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

classes_to_export = [
    export_amenity,
    # export_leisure,
    export_atm,
    export_healthcare,
    ]
any_classes = [export_shop, export_tourism, export_craft, export_office]
special_access_classes = [export_leisure,]

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
    "vending_machine": ["Automat","Verkaufsautomat"],
    "pitch": ["Sportplatz"],
    "golf_course": ["Golfplatz"],
    "horse_riding": ["Reitplatz"],
    "water_park": ["Schwimmbad"],
    "fitness_centre": ["Fitness Center"],
    "doctors": ["Arzt", "Doktor"],
    "doctor": ["Arzt", "Doktor"],
    "hospital": ["Spital", "Hospital", "Krankenhaus"],
    "dentist": ["Zahnarzt"],
    "marketplace": ["Marktplatz", "Bauernmarkt", "Markt"],
    "post_office": ["Post", "Postamt", "Paket", "Packerl", "Brief"],
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

yosm_types = {
    'amenity': {
        'type': 'unknown', # fallback type
        'restaurant': {
            'type': 'gastro',
            'label': 'Restaurant',
        },
        'cafe': {
            'type': 'gastro',
            'label': 'Cafe',
        },
        'fast_food': {
            'type': 'gastro',
            'label': 'Fast Food',
        },
        'biergarten': {
            'type': 'gastro',
            'label': '', # use value.capitalize()
        },
        'pub': {
            'type': 'gastro',
            'label': '',
        },
        'bar': {
            'type': 'gastro',
            'label': '',
        },
        'doctor': {
            'type': 'doctor',
            'label': 'Arzt',
        },
        'dentist': {
            'type': 'doctor',
            'label': 'Zahnarzt',
        },
        'physiotherapist': {
            'type': 'doctor',
            'label': 'Physiotherapeut',
        },
        'pharmacy': {
            'type': 'pharmacy',
            'label': 'Apotheke',
        },
        'atm': {
            'type': 'atm',
            'label': 'Bankomat',
        },
        'bank': {
            'type': 'bank',
            'label': '',
        },
        'vending_machine': {
            'type': 'vending_machine',
            'label': 'Verkaufs-Automat',
        },
        'fuel': {
            'type': 'fuel',
            'label': 'Tankstelle',
        },
        'marketplace': {
            'type': 'marketplace',
            'label': 'Marktplatz',
        },
        'post_office': {
            'type': 'post_office',
            'label': 'Post',
        },
    },
    'healthcare': {
        'type': 'doctor',
        'doctor': {
            'type': 'doctor',
            'label': 'Arzt',
        },
        'dentist': {
            'type': 'doctor',
            'label': 'Zahnarzt',
        },
        'physiotherapist': {
            'type': 'doctor',
            'label': 'Physiotherapeut',
        },
        'pharmacy': {
            'type': 'pharmacy',
            'label': 'Apotheke',
        },
    },
    'shop': {
        'type': 'shop',
        'hairdresser': {
            'type': 'hairdresser',
            'label': 'Friseur',
        },
        'supermarket': {
            'type': 'shop',
            'label': 'Supermarkt',
        },
        'clothes': {
            'type': 'shop',
            'label': 'Kleidung',
        },
        'bakery': {
            'type': 'shop',
            'label': 'Bäckerei',
        },
        'car': {
            'type': 'shop',
            'label': 'Autohaus',
        },
        'car_repair': {
            'type': 'shop',
            'label': 'Autowerkstatt',
        },
        'convenience': {
            'type': 'shop',
            'label': 'Lebensmittelgeschäft',
        },
    },
    'craft': {
        'type': 'craftsman', # for all of class craft that don't have type
        'carpenter': '',
        'plumber': '',
        'electrician': '',
        'painter': '',
        'photographer': '',
        'roofer': '',
        'gardener': '',
        'beekeper': '',
        'shoemaker': '',
        'tailor': '',
        'stonemason': '',
        'handicraft': '',
        'builder': '',
    },
    'tourism': {
        'type': 'tourism', # for all of type tourism that don't have type
        'hotel': {
            'type': 'hotel',
            'label': '',
        },
        'guest_house': {
            'type': 'hotel',
            'label': '',
        },
        'alpine_hut': {
            'type': 'hotel',
            'label': '',
        },
        'chalet': {
            'type': 'hotel',
            'label': '',
        },
        'apartment': {
            'type': 'hotel',
            'label': '',
        },
        'viewpoint': '',
        'picnic_site': '',
        'attraction': '',
        'artwork': '',
        'museum': '',
        'information': '',
    },
}

table = """sudo -u postgres psql  -d gis -c "\d planet_osm_point" | \
grep -A 500 osm_id | grep -B 500 \ way\   | grep -v way |\
 cut -d \| -f 1 | sed 's/ //g' | sed 's/^/"/g;s/$/", /;s/:/_/g'
"""

labels = [
    "osm_data_type",
    "osm_id",
    "addr_city",
    "addr_street",
    "addr_place",
    "addr_housename",
    "addr_housenumber",
    "addr_postcode",
    "addr_unit",
    "addr_interpolation",
    "opening_hours",
    "website",
    "contact_website",
    "twitter", # contact:twitter
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
    "name_de",
    "shop",
    "sport",
    "tourism",
    "craft",
    "atm",
    "cuisine",
    "operator",
    "office",
    "fax",
    "vending",
    "old_name",
    "access",
    "fee",
    "healthcare",
    "healthcare_speciality",
    "healthcare_speciality_de",
    "emergency",
    "wheelchair",
    "wifi",
    "internet_access",
    "diet_vegan",
    "diet_vegetarian",
    "takeaway",
    "wikipedia",
    "wikidata",
]

cuisine_replacements = {
    'vegetrian': 'vegetarisch',
    'italian': 'italienisch',
    'chinese': 'chinesisch',
    'french': 'französisch',
    'fish': 'Fisch',
    'chicken': 'Huhn',
    'asian': 'asiatisch',
    'cake': 'Kuchen & Torten',
    'austrian': 'österreichisch',
    'ice_cream': 'Eis',
    'german': 'deutsch',
    'african': 'afrikanisch',
    'coffee_shop': 'Kaffeehaus',
    'greek': 'griechisch',
    'alpine_hut': 'Almhütte',
    'turkish': 'türkisch',
    'indian': 'indisch',
    'japanese': 'japanisch',
    'mexican': 'mexikanisch'
}

healthcare_replacements = {
    'general': 'allgemeine Medizin',
    'gynaecology': 'Gynäkologie',
    'internal': 'Innere Medizin',
    'ophthalmology': 'Augenheilkunde',
    'orthopaedics': 'Orthopädie',
    'paediatrics': 'Kinderheilkunde',
    'surgery': 'Chirurgie',
    'otolaryngology': 'Hals-Nasen-Ohren-Heilkunde',
    'urology': 'Urologie'
}

vending_replacements = {
    'parking_tickets': 'Parkscheine',
    'excrement_bags': 'Hundekotsackerl',
    'public_transport_tickets': 'Öffitickets',
    'cigarettes': 'Zigaretten',
    'sweets': 'Süßigkeiten',
    'newspapers': 'Zeitungen',
    'chewing_gums': 'Kaugummi'
}

def read_line_from_csv():
    # format: name1,lon,lat,type1,*
    with open(EXPORT_FILE,'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for line in reader:
            if not line:
                continue
            yield line

def split_and_translate(tr_str, translations):
    strings = tr_str.split(';')
    str_temp = []
    for s in strings:
        if s in translations:
            str_temp.append(translations[s])
        else:
            str_temp.append(s)
    return(", ".join(str_temp))


osm_ids = {}
yosm_type = None
yosm_subtype = None
with open(EXPORT_ES_FILE,'w') as out:
    print("Export ES json:")
    for line in read_line_from_csv():
        if not line[1]:
            continue
        # only export osm_id once
        if line[5] in osm_ids:
            continue
        else:
            osm_ids[line[5]] = True

        name = line[0]
        desc = line[3]
        label_dict = {label: value for label,value in zip(labels,line[4:]) if value}

        if 'atm' in label_dict and \
            ( label_dict['atm'] == 'no' or \
            label_dict['atm'] == 'false' ): # wrong label, but we don't want it in the index
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

        try:
            for osmtype, _ in yosm_types.items():
                if osmtype in label_dict:
                    # print("="*75)
                    # print(label_dict[osmtype])
                    if label_dict[osmtype] in yosm_types[osmtype] and \
                        label_dict[osmtype] in yosm_types[osmtype] and \
                        'type' in yosm_types[osmtype][label_dict[osmtype]]:

                        # print("label_dict: " + label_dict[osmtype]) # hotel, pharmacy
                        # print(yosm_types[osmtype])
                        # print(yosm_types[osmtype][label_dict[osmtype]])
                        yosm_type = yosm_types[osmtype][label_dict[osmtype]]['type']
                    else:
                        yosm_type = yosm_types[osmtype]['type']
                        # print(yosm_types[osmtype])

                    # print("yosm_type: " + yosm_type)

                    if not label_dict[osmtype] in yosm_types[osmtype] or \
                        not 'label' in yosm_types[osmtype][label_dict[osmtype]] or \
                        not yosm_types[osmtype][label_dict[osmtype]]['label']:

                        yosm_subtype = " ".join(label_dict[osmtype].capitalize().split('_'))
                        # print("yosm_subtype: " + yosm_subtype)
                    else:
                        yosm_subtype = " ".join(yosm_types[osmtype][label_dict[osmtype]]['label'].capitalize().split('_'))
                        # print("yosm_subtype: " + yosm_subtype)

        except KeyError as ex:
            print(label_dict)
            print("Key Error {}, {}, {}".format(ex, osmtype, label_dict))
            raise

        if "name_de" in label_dict:
            label_dict['name'] = label_dict['name_de']
            del label_dict['name_de']
        if "description_de" in label_dict:
            label_dict['description_de'] = label_dict['description_de']
            del label_dict['description_de']
        if "smoking" in label_dict:
            if label_dict['smoking'] in ['dedicated','yes','separated']:
                label_dict['smoking'] = 'yes'
            else:
                label_dict['smoking'] = 'no'
        # wheelchair leave the same

        if 'wifi' in label_dict and \
            label_dict['wifi'] in ['yes','free']:
            label_dict['wifi'] = 'yes'
        if 'internet_access' in label_dict and \
            label_dict['internet_access'] in ['wlan','yes']:
            label_dict['wifi'] = 'yes'
            del label_dict['internet_access']

        if 'diet_vegan' in label_dict:
            if label_dict['diet_vegan'] in ['yes','only']:
                label_dict['vegan'] = 'yes'
                label_dict['vegetrian'] = 'yes'
                del label_dict['diet_vegan']
        if 'diet_vegetarian' in label_dict:
            if label_dict['diet_vegetarian'] in ['yes','only']:
                label_dict['vegetrian'] = 'yes'
                del label_dict['diet_vegetarian']

        # takeaway leave the same

        # atm leave the same

        # leave phone the same
        # just overwrite if contact_phone present
        if 'contact_phone' in label_dict:
            label_dict['phone'] = label_dict['contact_phone']
            del label_dict['contact_phone']

        # leave website the same
        # just overwrite if contact_website present
        if 'contact_website' in label_dict:
            label_dict['website'] = label_dict['contact_website']
            del label_dict['contact_website']
        if 'contact_facebook' in label_dict and \
            not 'website' in label_dict:
            label_dict['website'] = label_dict['contact_facebook']
            del label_dict['contact_facebook']

        #  addr
        if 'addr_street' in label_dict:
            street = label_dict['addr_street']
        else:
            street = ""
        if 'addr_place' in label_dict:
            place = label_dict['addr_place']
        else:
            place = ""
        if 'addr_housenumber' in label_dict:
            hnumber = label_dict['addr_housenumber']
        else:
            hnumber = ""
        if 'addr_unit' in label_dict:
            unit = label_dict['addr_unit']
        else:
            unit = ""
        if 'addr_postcode' in label_dict:
            postcode = label_dict['addr_postcode']
        else:
            postcode = ""
        if 'addr_city' in label_dict:
            city = label_dict['addr_city']
        else:
            city = ""

        # TODO delete addr: fields from final ES import

        # unit is optional
        label_dict['address'] = (street or place) + \
            ((' ' + hnumber) if hnumber else '') + \
            ((' ' + unit) if unit else '') + \
            ((', ' + postcode) if postcode else '') + \
            ((' ' + city) if city else '')
        if not label_dict['address']:
            del label_dict['address']
        elif not (street or place) or \
            not hnumber or \
            not postcode or \
            not city:
            label_dict['address_incomplete'] = True
            label_dict['address'] = label_dict['address'].strip()


        # wikidata leave the same
        # wikipedia leave the same

        # if 'cuisine' in label_dict and \
        #     label_dict['cuisine'] in cuisine_replacements:
        #     label_dict['cuisine'] = cuisine_replacements[label_dict['cuisine']]
        if 'cuisine' in label_dict:
            label_dict['cuisine'] = split_and_translate(label_dict['cuisine'], cuisine_replacements)

        if 'vending' in label_dict and \
            label_dict['vending'] in vending_replacements:
            label_dict['vending'] = vending_replacements[label_dict['vending']]
        if 'healthcare_speciality' in label_dict:
            label_dict['healthcare_speciality'] = split_and_translate(label_dict['healthcare_speciality'], healthcare_replacements)

        if 'healthcare_speciality_de' in label_dict:
            label_dict['healthcare_speciality'] = ", ".join(label_dict['healthcare_speciality_de'].split(';'))
            del label_dict['healthcare_speciality_de']

        if label_dict['osm_data_type'] == 'n': # node
            label_dict['osm_data_type'] = 'node'
        elif label_dict['osm_data_type'] == 'w':
            if int(label_dict['osm_id']) < 0: # relation
                label_dict['osm_data_type'] = 'relation'
                label_dict['osm_id'] = abs(int(label_dict['osm_id']))
            else: # way
                label_dict['osm_data_type'] = 'way'

        # operator

        # stars

        out.write(json.dumps({"index": {}}) + "\n")
        lat = float(line[2])
        lon = float(line[1])
        # # print({"name": line[0], "location": [lon,lat], "description": line[3]})
        # print(json.dumps({"name": name, "location": [lon,lat], "description": desc}))
        if yosm_type:
            out.write(json.dumps({"name": name, "location": [lon,lat], "type": yosm_type, "subtype": yosm_subtype, "description": desc, "labels": label_dict}) + "\n")
        else:
            out.write(json.dumps({"name": name, "location": [lon,lat], "description": desc, "labels": label_dict}) + "\n")
