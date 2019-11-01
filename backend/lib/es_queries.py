"""ES queries in JSON format for the API"""
import json


def get_es_filter(bounding_box):
    top_left_lat, top_left_lon, bottom_right_lat, bottom_right_lon = bounding_box
    return {
        "geo_bounding_box": {
            "location": {
                "top_left": {"lat": float(top_left_lat), "lon": float(top_left_lon)},
                "bottom_right": {
                    "lat": float(bottom_right_lat),
                    "lon": float(bottom_right_lon),
                },
            }
        }
    }


def es_standard_search(query, es_filter, limit=10000):
    return json.dumps(
        {
            "size": int(limit),
            "query": {
                "bool": {
                    "should": [
                        {
                            "query_string": {
                                "query": f"{query}*",
                                "default_operator": "AND",
                                "fields": [
                                    "labels.name^5",
                                    "description^50",
                                    #   // 'labels.website^3',
                                    #   // 'labels.contact_website',
                                    "labels.addr_street",
                                    "labels.addr_city",
                                    "labels.amenity",
                                    "labels.craft",
                                    "labels.emergency",
                                    "labels.healthcare",
                                    "labels.healthcare_speciality",
                                    "labels.leisure",
                                    "labels.shop",
                                    "labels.sport",
                                    "labels.tourism",
                                    "labels.vending",
                                    "labels.cuisine^5",
                                ],
                            }
                        }
                    ],
                    "minimum_should_match": 1,
                    "filter": es_filter,
                }
            },
        }
    )


def es_city_search(query, city, limit=10000):
    return json.dumps(
        {
            "size": int(limit),
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": f"{query}*",
                                "default_operator": "OR",
                                "fields": [
                                    "labels.name^5",
                                    "description^50",
                                    # "labels.website^3",
                                    # "labels.contact_website",
                                    "labels.addr_street",
                                    # "labels.addr_city",
                                    "labels.amenity",
                                    "labels.craft",
                                    "labels.emergency",
                                    "labels.healthcare",
                                    "labels.healthcare_speciality",
                                    "labels.leisure",
                                    "labels.shop",
                                    "labels.sport",
                                    "labels.tourism",
                                    "labels.vending",
                                    "labels.cuisine^5",
                                ],
                            }
                        },
                        {
                            "query_string": {
                                "query": f"{city}",
                                "fields": ["labels.addr_city"],
                            }
                        },
                    ]
                }
            },
        }
    )
