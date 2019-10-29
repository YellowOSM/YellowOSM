"""YOSM_POI YellowOSM POI class to hold and maniputlate OSM data"""
import reverse_geocode

from csv_labels import (
    labels,
    translated_info,
    yosm_types,
    cuisine_replacements,
    healthcare_replacements,
    vending_replacements,
)


class YOSM_POI:
    def __init__(self, csv):
        self._csv = csv
        self.name = None
        self.lat = None
        self.lon = None
        self.yosm_type = None
        self.yosm_subtype = None
        self.country = None
        self.country_code = None
        self.label_dict = {}
        self._load_csv(csv)
        if self._filter_and_tag_poi():
            return
        self._translate_poi()
        self._estimate_and_set_country(self.lat, self.lon)
        self._cleanup_labels()

    def _load_csv(self, line):
        self.name = line[0]
        self.lat = float(line[2])
        self.lon = float(line[1])
        self.desc = line[3]
        self.label_dict = {
            label: value for label, value in zip(labels, line[4:]) if value
        }

        if not self.name and self.desc:
            self.name = (
                translated_info[self.desc][0]
                if self.desc in translated_info
                else self.desc.capitalize()
            )

        if "amenity" in self.label_dict and self.label_dict["amenity"] == "atm":
            self.label_dict["atm"] = "yes"
        if "atm" in self.label_dict and (
            self.label_dict["atm"] == "no" or self.label_dict["atm"] == "false"
        ):  # wrong label, but we don't want it in the index
            del self.label_dict["atm"]
        if "atm" in self.label_dict and self.label_dict["atm"] != "no":
            self.desc += " " + " ".join(translated_info["atm"])
        # set Bankomat as name if no name is given:
        if "atm" in self.label_dict and "name" not in self.label_dict:
            self.label_dict["name"] = translated_info["atm"][0]
            self.name = translated_info["atm"][0]

        for typus in ["amenity", "leisure", "shop", "craft", "tourism"]:
            if typus in self.label_dict and self.label_dict[typus] in translated_info:

                self.desc += " " + " ".join(translated_info[self.label_dict[typus]])
            # if self.label_dict[subtype]

        try:
            for osmtype, _ in yosm_types.items():
                if osmtype in self.label_dict:
                    # print("="*75)
                    # print(label_dict[osmtype])
                    if osmtype.lower() in ["office"]:
                        self.yosm_subtype = None
                        continue

                    if (
                        self.label_dict[osmtype] in yosm_types[osmtype]
                        and "type" in yosm_types[osmtype][self.label_dict[osmtype]]
                    ):

                        # print("label_dict: " + label_dict[osmtype]) # hotel, pharmacy
                        # print(yosm_types[osmtype])
                        # print(yosm_types[osmtype][label_dict[osmtype]])
                        self.yosm_type = yosm_types[osmtype][self.label_dict[osmtype]][
                            "type"
                        ]
                    else:
                        self.yosm_type = yosm_types[osmtype]["type"]
                        # print(yosm_types[osmtype])

                    # print("yosm_type: " + yosm_type)

                    if (
                        not self.label_dict[osmtype] in yosm_types[osmtype]
                        or "label" not in yosm_types[osmtype][self.label_dict[osmtype]]
                        or not yosm_types[osmtype][self.label_dict[osmtype]]["label"]
                    ):

                        if self.label_dict[osmtype] in translated_info:
                            self.yosm_subtype = " ".join(
                                translated_info[self.label_dict[osmtype]][0]
                                .capitalize()
                                .split("_")
                            )
                        else:
                            self.yosm_subtype = " ".join(
                                self.label_dict[osmtype].capitalize().split("_")
                            )
                        # print("yosm_subtype: " + yosm_subtype)
                    else:
                        self.yosm_subtype = " ".join(
                            yosm_types[osmtype][self.label_dict[osmtype]]["label"]
                            .capitalize()
                            .split("_")
                        )
                        # print("yosm_subtype: " + yosm_subtype)

                    # stop type search after first hit
                    break

        except KeyError as ex:
            print(self.label_dict)
            print("Key Error {}, {}, {}".format(ex, osmtype, self.label_dict))
            raise

    def _translate_poi(self):
        # use german name or desc if it exists
        if "name_de" in self.label_dict:
            self.label_dict["name"] = self.label_dict["name_de"]
            del self.label_dict["name_de"]
        if "description_de" in self.label_dict:
            self.label_dict["description_de"] = self.label_dict["description_de"]
            del self.label_dict["description_de"]

        # simplify smoking # TODO fix in the future
        if "smoking" in self.label_dict:
            if self.label_dict["smoking"] in ["dedicated", "yes", "separated"]:
                self.label_dict["smoking"] = "yes"
            else:
                self.label_dict["smoking"] = "no"

        # wheelchair leave the same

        # we know internet and wifi are not the same (but we only show a wifi logo)
        if "wifi" in self.label_dict and self.label_dict["wifi"] in ["yes", "free"]:
            self.label_dict["wifi"] = "yes"
        if "internet_access" in self.label_dict and self.label_dict[
            "internet_access"
        ] in ["wlan", "yes"]:
            self.label_dict["wifi"] = "yes"
            del self.label_dict["internet_access"]

        # vegetarian is ok if it is vegan
        if "diet_vegan" in self.label_dict:
            if self.label_dict["diet_vegan"] in ["yes", "only"]:
                self.label_dict["vegan"] = "yes"
                self.label_dict["vegetarian"] = "yes"
                del self.label_dict["diet_vegan"]
        if "diet_vegetarian" in self.label_dict:
            if self.label_dict["diet_vegetarian"] in ["yes", "only"]:
                self.label_dict["vegetarian"] = "yes"
                del self.label_dict["diet_vegetarian"]

        # takeaway leave the same

        # atm leave the same

        # leave phone the same
        # just overwrite if contact_phone present
        if "contact_phone" in self.label_dict:
            self.label_dict["phone"] = self.label_dict["contact_phone"]
            del self.label_dict["contact_phone"]

        # only use contact_mobile if contact_phone or phone not present
        if "phone" not in self.label_dict and "contact_mobile" in self.label_dict:
            self.label_dict["phone"] = self.label_dict["contact_mobile"]
            del self.label_dict["contact_mobile"]

        # contact_fax is the same, but get fax if contact_fax is missing
        if "contact_fax" not in self.label_dict and "fax" in self.label_dict:
            self.label_dict["contact_fax"] = self.label_dict["fax"]
            del self.label_dict["fax"]

        # contact_email is the same, but get email if contact_email is missing
        if "contact_email" not in self.label_dict and "email" in self.label_dict:
            self.label_dict["contact_email"] = self.label_dict["email"]
            del self.label_dict["email"]

        # leave website the same
        # just overwrite if contact_website present
        if "contact_website" in self.label_dict:
            self.label_dict["website"] = self.label_dict["contact_website"]
            del self.label_dict["contact_website"]

        # if only a facebook page is given, consider that the website
        if "contact_facebook" in self.label_dict and "website" not in self.label_dict:
            self.label_dict["website"] = self.label_dict["contact_facebook"]
            del self.label_dict["contact_facebook"]

        # fix missing http
        if "website" in self.label_dict:
            if not self.label_dict["website"].startswith("http"):
                self.label_dict["website"] = "http://" + self.label_dict["website"]

        #  addr
        if "addr_street" in self.label_dict:
            street = self.label_dict["addr_street"]
        else:
            street = ""
        if "addr_place" in self.label_dict:
            place = self.label_dict["addr_place"]
        else:
            place = ""
        if "addr_housenumber" in self.label_dict:
            hnumber = self.label_dict["addr_housenumber"]
        else:
            hnumber = ""
        if "addr_unit" in self.label_dict:
            unit = self.label_dict["addr_unit"]
        else:
            unit = ""
        if "addr_postcode" in self.label_dict:
            postcode = self.label_dict["addr_postcode"]
        else:
            postcode = ""
        if "addr_city" in self.label_dict:
            city = self.label_dict["addr_city"]
        else:
            city = ""
        # if 'addr_country' in self.label_dict:
        #     country = self.label_dict['addr_country']
        # else:
        #     country = ""

        # unit is optional
        self.label_dict["address"] = (
            (street or place)
            + ((" " + hnumber) if hnumber else "")
            + ((" " + unit) if unit else "")
            + ((", " + postcode) if postcode else "")
            + ((" " + city) if city else "")
        )
        if not self.label_dict["address"]:
            del self.label_dict["address"]
        elif not (street or place) or not hnumber or not postcode or not city:
            self.label_dict["address_incomplete"] = True
            self.label_dict["address"] = self.label_dict["address"].strip()

        # wikidata leave the same
        # wikipedia leave the same

        # if 'cuisine' in self.label_dict and \
        #     self.label_dict['cuisine'] in cuisine_replacements:
        #     self.label_dict["cuisine"] =
        #         cuisine_replacements[self.label_dict["cuisine"]]
        if "cuisine" in self.label_dict:
            self.label_dict["cuisine"] = self._split_and_translate(
                self.label_dict["cuisine"], cuisine_replacements
            )

        if (
            "vending" in self.label_dict
            and self.label_dict["vending"] in vending_replacements
        ):
            self.label_dict["vending"] = vending_replacements[
                self.label_dict["vending"]
            ]

        # dentists may appear in amenity:
        if "amenity" in self.label_dict and self.label_dict["amenity"] == "dentist":
            self.label_dict["healthcare_speciality"] = self._split_and_translate(
                "dentist", healthcare_replacements
            )

        if "healthcare_speciality" in self.label_dict:
            self.label_dict["healthcare_speciality"] = self._split_and_translate(
                self.label_dict["healthcare_speciality"], healthcare_replacements
            )

        if "healthcare_speciality_de" in self.label_dict:
            self.label_dict["healthcare_speciality"] = ", ".join(
                self.label_dict["healthcare_speciality_de"].split(";")
            )
            del self.label_dict["healthcare_speciality_de"]

        if "sport" in self.label_dict:
            d = ", ".join(
                s.replace("_", " ").title() for s in self.label_dict["sport"].split(";")
            )
            self.label_dict["sport"] = d

        if self.label_dict["osm_data_type"] == "n":  # node
            self.label_dict["osm_data_type"] = "node"
        elif self.label_dict["osm_data_type"] == "w":
            if int(self.label_dict["osm_id"]) < 0:  # relation
                self.label_dict["osm_data_type"] = "relation"
                self.label_dict["osm_id"] = abs(int(self.label_dict["osm_id"]))
            else:  # way
                self.label_dict["osm_data_type"] = "way"

    def _split_and_translate(self, tr_str, translations):
        strings = tr_str.split(";")
        str_temp = []
        for s in strings:
            if s in translations:
                str_temp.append(translations[s])
            else:
                str_temp.append(s.replace("_", " ").title())
        return ", ".join(str_temp)

    def _estimate_and_set_country(self, lat, lon):
        """Estimate the country a POI is in and set it as property"""
        if "addr_country" not in self.label_dict:
            data = reverse_geocode.search([(float(lat), float(lon))])
            self.label_dict["addr_country"] = data[0]["country_code"]

    def _cleanup_labels(self):
        """Remove labels that are not needed"""
        blacklist = ["building"]
        for bad_label in blacklist:
            self.label_dict.pop(bad_label, None)

    def _filter_and_tag_poi(self):
        # clean up building type:
        # building of commercial use should have at least a name to be in the index
        if "building" == self.yosm_type:
            if self.name.lower() in yosm_types["building"]:
                self.label_dict["dont_import"] = True
                return True
        return False
