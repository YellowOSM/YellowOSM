This crawler takes a list of OSM IDs and attempts to find missing contact e-mail addresses. Any OSM IDs in the input 
file that have a website but do not have an e-mail address are craweld and then searched for a possible e-mail address.
This address is accepted as a very likely match if a) it is the only one on the website and b) if the part after the @
matches the website's hostname (e.g., contact@yosm.com if that was found on www.yosm.com).
These very likely matches can then be uploaded to maproulette.com for users to double-check.

# Prerequisites
* A MySQL user yellowosm with password yellowosm and all rights on a database called yellowosm
* scrapy

Execute the following steps:

* place an input file in data/input (like osm_es_export_sample.json)
* run `scrapy yosm_init_db` to initialize the database
* run `scrapy yosm_preprocess` to preprocess this input file and filter out only relevant OSM IDs
* run `scrapy crawl yellowosm` to crawl websites (warning: this is gonna take a while)
* run `scrapy yosm_postprocess` to extract e-mail addresses from the crawled websites
* run `scrapy yosm_postprocess_maproulette` to build a MapRoulette challenge
* upload this challenge to maproulette.com
