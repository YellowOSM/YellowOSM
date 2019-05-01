"""labels used for the csv export. order is significant.
order derives from `backend/scripts/osm2pgsql/yosm.style`, but also from the
queries in `backend/scripts/export_osm_to_elasticsearch.py`
"""

# get an INCOMPLETE list of labels from the DB:
# the DB queries will add additional elements
# table = """sudo -u postgres psql  -d gis -c "\d planet_osm_point" | \
# grep -A 500 osm_id | grep -B 500 \ way\   | grep -v way |\
#  cut -d \| -f 1 | sed 's/ //g' | sed 's/^/"/g;s/$/", /;s/:/_/g'
# """

labels = [ # order important!
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

translated_info = {
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
    "post_box": ["Postkasten", "Briefkasten"],
    "telephone": ["Telefon", "Telefonzelle", "Telephon"],
    # "": ["",],
}

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
    'office': {
        'type': 'office',
    }
}

cuisine_replacements = {
    'vegetarian': 'vegetarisch',
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
