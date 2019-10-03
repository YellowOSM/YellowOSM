"""ES queries in JSON format for the API"""
import json
import urllib.parse


def es_standard_search(query, es_filter):
    return json.dumps(
        {
            "size": 300,
            "query": {
                "bool": {
                    "should": [
                        {
                            "query_string": {
                                "query": f"{query}",
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


def es_city_search(query, city):
    return json.dumps(
        {
            "size": 300,
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": f"{query}*",
                                "default_operator": "OR",
                                "fields": [
                                    "labels.name^50",
                                    "description",
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
