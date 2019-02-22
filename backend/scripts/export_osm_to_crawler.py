#!/usr/bin/python3
import os
import json
import csv
# import argparse

# don't do the next line yet, it will run the complete script
## from export_osm_to_elasticsearch import labels as labels
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
    "cuisine",
    "operator",
    "office",
    "fax",
    "vending",
    "old_name",
    "access",
    "fee",
    "healthcare",
    "healthcare:speciality",
    "emergency",
]

## needs export_osm_to_elasticsearch to run first!
csv.field_size_limit(100000000)

# parser = argparse.ArgumentParser()
# parser.add_argument('--local',action="store_true", help="run script in local context without docker postgres")
#
# args = vars(parser.parse_args())
# SERVER = not args['local']

EXPORT_FILE = "/tmp/dump.osm"
EXPORT_ES_FILE = "/tmp/osm_crawler.json"

# also export polygons
poly = True
# poly = False
query_db = False
LIMIT = 100000000000
# LIMIT = 10

# # additional info:
# # first element will be alternative name!!
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
    # "": ["",],
}

def read_line_from_csv():
    # format: name1,lon,lat,type1,*
    with open(EXPORT_FILE,'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for line in reader:
            if not line:
                continue
            yield line

osm_ids = {}
with open(EXPORT_ES_FILE,'w') as out:
    print("Export real json:") # assemble by hand
    out.write('{\n')
    not_next = True
    for line in read_line_from_csv():
        if not not_next:
            out.write(',\n')
        else:
            not_next = False

        # only export osm_id once
        if line[4] in osm_ids:
            not_next = True
            continue
        else:
            osm_ids[line[4]] = True

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

        if not line[1]:
            not_next = True
            continue
        if not ('website' in label_dict or 'contact_website' in label_dict):
            not_next = True
            continue
        lat = float(line[2])
        lon = float(line[1])
        # # print({"name": line[0], "location": [lon,lat], "description": line[3]})
        # print(json.dumps({"name": name, "location": [lon,lat], "description": desc}))
        out.write(json.dumps({"name": name, "location": [lon,lat], "description": desc, "labels": label_dict}))
    out.write('}')
