"""YellowOSM Backend - API.

.. moduleauthor:: Florian Klien <flowolf@klienux.org>

"""

import json
import logging
import os
import urllib.parse

import requests
import responder
from marshmallow import Schema, fields
from dotenv import load_dotenv
import geoip2.database

from lib.geo58 import Geo58

from lib.es_queries import es_standard_search, es_city_search, get_es_filter


cities_bb_file = "data/cities_bb.json"
cities_bb = {}
with open(cities_bb_file) as f:
    cities_bb = json.loads(f.read())


logger = logging.getLogger("api")


# logger.setLevel(logging.DEBUG)
# with no handlers:
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

load_dotenv()
DEBUG = os.getenv("DEBUG", default=False)
SHORT_URL_REDIRECT_URL = os.getenv("SHORT_URL_REDIRECT_URL")
API_URL = os.getenv("API_URL")
DEFAULT_ZOOM_LEVEL = os.getenv("DEFAULT_ZOOM_LEVEL", default=19)
ES_URL = os.getenv("ES_URL")
ES_INDEX = os.getenv("ES_INDEX", default="yosm")


contact = {
    "name": "YellowOSM",
    "url": "https://yellowosm.com/#contact"
    # "email": "",
}

license = {
    "name": "GNU AGPL v3.0",
    "url": "https://www.gnu.org/licenses/agpl-3.0.en.html",
}

GIT_HASH = "dev"

try:
    # .git_commit_hash.txt should be populated in deploy process
    GIT_HASH = open(".git_commit_hash.txt", "r").read()
except Exception:
    pass

YOSM_VERSION = "0.4b1"
VERSION = YOSM_VERSION + "_" + GIT_HASH
DESC = """# YellowOSM API

more information about YellowOSM and the API that lies behind these calls can be found
in our
[Github Repo](https://github.com/YellowOSM/YellowOSM/tree/master/backend#backend-yellowosm)

The API allows to search YellowOSM data, resolve and create Geo58 short-strings and get
data or vcards for specific osmIDs.

[YellowOSM - Repository](https://github.com/YellowOSM/YellowOSM)

[YellowOSM - Backend](https://github.com/YellowOSM/YellowOSM/tree/master/backend)

[YellowOSM - Frontend/Map](https://github.com/YellowOSM/YellowOSM/tree/master/frontend)
"""

api = responder.API(
    debug=DEBUG,
    version=VERSION,
    cors=True,
    cors_params={
        "allow_origins": ["*"],
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    },
    openapi="3.0.2",
    docs_route="/api/docs",
    description=DESC,
    # openapi_route="/schema.yml",
    contact=contact,
    license=license,
)


logger.info("debug: " + DEBUG)
if DEBUG:
    logger.setLevel("DEBUG")
else:
    logger.setLevel("WARNING")
logger.debug("short url: " + SHORT_URL_REDIRECT_URL)


@api.schema("coordinates")
class CoordSchema(Schema):
    lat = fields.Float()
    lon = fields.Float()


@api.schema("XYCoordinates")
class XYCoordSchema(Schema):
    x = fields.Float()
    y = fields.Float()
    zoom = fields.Float()


@api.schema("Geo58-Short")
class Geo58ShortString(Schema):
    geo58 = fields.String()


@api.schema("POI")
class POISchema(Schema):
    osmid = fields.Int()
    osm_data_type = ["node", "way"]
    location = fields.Nested(CoordSchema)
    # location = fields.Pluck(CoordSchema, 'lat')
    name = fields.Str()
    addr_city = fields.Str()
    addr_street = fields.Str()
    addr_housenumber = fields.Str()
    addr_postcode = fields.Str()
    addr_country = fields.Str()
    address = fields.Str()
    opening_hours = fields.Str()
    website = fields.Str()
    phone = fields.Str()
    shop = fields.Str()
    amenity = fields.Str()
    contact_email = fields.Str()


@api.route("/api/")
@api.route("/api/hello")
def hello_world(req, resp):
    resp.text = (
        "Hello! You are looking at the backend of YellowOSM.com. It's nice isn't it? \n"
        "Do you want to see how we made it? Go to the source code: https://github.com/"
        "YellowOSM/YellowOSM. \n\n"
        "The API-Documentation can be found here: https://yellowosm.com/api-docs/\n\n"
        "We are currently running version {}\n\n"
        "If you don't know what all this means, the interwebz redirected you here by"
        " mistake.\nMore Information about the project can be found here: "
        "https://yellowosm.com".format(VERSION)
    )


@api.route("/api/coords_to_geo58/{zoom}/{x}/{y}")  # legacy
async def convertCoordsToGeo58_old(req, resp, *, zoom, x, y):
    """legacy function: convert zoom, x, y to a Geo58 string
    (use /api/geo58/{zoom}/{x}/{y} instead)
    """
    return await convertCoordsToGeo58(req, resp, zoom=zoom, x=x, y=y)


@api.route("/api/geo58/{zoom}/{x}/{y}")
async def convertCoordsToGeo58(req, resp, *, zoom, x, y):
    """convert zoom, x, y to a Geo58 string
    ---
    get:
        summary: get Geo58 short-string
        description: convert coordinates `z`/`x`/`y` to Geo58 short-string.
        responses:
            '200':
                description: get corresponding Geo58 short-string
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/Geo58-Short'
            '406':
                description: coordinates invalid.
        parameters:
        -   name: x
            in: path
            required: true
            description: latitude from -90 to 90
            schema:
                type: number
            example: 47.07424
        -   name: y
            in: path
            description: longitude from -180 to 180
            required: true
            schema:
                type: number
            example: 15.43258
        -   name: zoom
            in: path
            description: |
              zoom level to be encoded in Geo58 String. must be between 5 and 20.
            required: true
            schema:
                type: integer
            example: 20
    """
    try:
        g58 = Geo58(zoom=zoom, lat=x, lon=y.strip(" /"))
    except Geo58.Geo58Exception as ex:
        logger.debug(
            "Error: coords_to_geo58: Not Acceptable: coordinates invalid. [%s]", ex
        )
        resp.status_code = 406
        text = "Error: Not Acceptable: coordinates invalid. [{}]".format(ex)
        resp.media = {"error": text}
        return
    resp.media = {"geo58": g58.get_geo58()}


@api.route("/api/geo58_to_coords/{geo58_str}")  # legacy
async def convertGeo58ToCoords_old(req, resp, *, geo58_str):
    """legacy function: convert zoom, x, y to a Geo58 string
    (use /api/geo58/{geo58_str} instead)
    """
    return await convertGeo58ToCoords(req, resp, geo58_str=geo58_str)


@api.route("/api/geo58/{geo58_str}")
async def convertGeo58ToCoords(req, resp, *, geo58_str):
    """convert zoom, x, y to a Geo58 string
    ---
    get:
        summary: get coordinates `z`/`x`/`y`
        description: convert Geo58 short-string to coordinates `z`/`x`/`y`.
        responses:
            '200':
                description: get corresponding coordinates `z`/`x`/`y`.
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/XYCoordinates'
            '400':
                description: invalid Geo58 short-code.
        parameters:
        -   name: geo58_str
            in: path
            required: true
            schema:
                type: string
            example: 4dHEj1AKm
    """
    try:
        g58 = Geo58(g58=geo58_str)
    except Geo58.Geo58Exception as ex:
        logger.debug("Error: geo58_to_coords: invalid short code: %s", ex)
        resp.status_code = 400
        text = "Error: Bad Request: invalid short code. [{}]".format(ex)
        resp.media = {"error": text}
        return
    zoom, x, y = g58.get_coordinates()
    resp.media = {"zoom": zoom, "x": x, "y": y}


@api.route("/api/redirect_geo58/")
async def convertGeo58ToCoordsEmpty(req, resp):
    """redirect to map without coords"""
    redir_url = "/".join(SHORT_URL_REDIRECT_URL.split("/")[:-3])
    logger.debug("redirect to --> %s", redir_url)
    resp.status_code = 301
    resp.headers["Location"] = redir_url


@api.route("/api/redirect_geo58/{geo58_str}")
async def redirect_geo58(req, resp, *, geo58_str):
    """redirect Geo58 string to corresponding z/x/y map URL
    ---
    get:
        summary: redirect to YellowOSM map
        description: redirects to YellowOSM map with given short-string.
            this will resolve the short-string and redirect to coordinates (`z`/`x`/`y`).
        responses:
            '302':
                description: redirect
            '400':
                description: invalid short code
        parameters:
        -   name: geo58_str
            in: path
            required: true
            schema:
                type: string
            example: 4dHEj1AKm
    """
    geo58_str = str(geo58_str)
    index = geo58_str.find(";", 0, 12)
    appendix = "" if index == -1 else str(geo58_str[index:])
    geo58 = geo58_str if index == -1 else geo58_str[:index]
    try:
        g58 = Geo58(g58=geo58)
    except Geo58.Geo58Exception as ex:
        logger.debug("redirect_geo58: invalid short code: %s", ex)
        resp.status_code = 400
        resp.text = "Error: Bad Request: invalid short code. [{}]".format(ex)
        return
    zoom, x, y = g58.get_coordinates()
    zoom = DEFAULT_ZOOM_LEVEL if zoom == 20 else zoom
    if not SHORT_URL_REDIRECT_URL:
        logger.error(
            "ERROR: no short url redirect url found! (add SHORT_URL_REDIRECT_URL to env)"
        )
        raise ValueError(
            "ERROR: no short url redirect url found! (add SHORT_URL_REDIRECT_URL to env)"
        )
    logger.debug((SHORT_URL_REDIRECT_URL, zoom, x, y, appendix))
    redir_url = SHORT_URL_REDIRECT_URL.format(zoom=zoom, x=x, y=y) + appendix
    logger.debug("redirect to --> %s", redir_url)
    resp.status_code = 302
    resp.headers["Location"] = redir_url


async def get_poi_info(req, resp, osm_id):
    url = ES_URL + "/" + ES_INDEX + "/_search"
    es_query = json.dumps(
        {
            "size": 1,
            "query": {
                "bool": {
                    "should": [
                        {"query_string": {"query": osm_id, "fields": ["labels.osm_id"]}}
                    ],
                    "minimum_should_match": 1,
                }
            },
        }
    )
    try:
        r = requests.get(
            url, data=es_query, headers={"Content-Type": "application/json"}
        )
    except (ConnectionError, requests.exceptions.ConnectionError) as ex:
        resp.status_code = 504
        logger.error(ex)
        text = "error: could not connect to database."
        resp.media = {"error": text}
    if json.loads(r.text)["hits"]["total"]["value"] == 0:
        resp.status_code = 404
        text = "error: no data found."
        resp.media = {"error": text}
    return (r, resp)


@api.route("/api/get_vcard/{osm_id}")  # legacy
async def get_vcard_old(req, resp, *, osm_id):
    """legacy function: Get a vcard download for the given osm_id
    (use /api/osmid/{osm_id}.vcard instead)
    """
    return await get_vcard(req, resp, osm_id=osm_id)


@api.route("/api/osmid/{osm_id}.vcard")
async def get_vcard(req, resp, *, osm_id):
    """Get a vcard download for the given osm_id
    ---
    get:
        summary: get vcard
        description: returns a vcard for the given `osm_id`
        responses:
            '200':
                description: OK
                content:
                    text/vcard:
                        schema:
                            $ref: '#/components/schemas/POI'
            '404':
                description: osm_id not found
            '504':
                description: could not connect to database
        parameters:
        -   name: osm_id
            in: path
            description: osmID, same as on OpenStreetMap.
            required: true
            schema:
                type: integer
            # example: 6930351827
            example: 317335810
    """

    r, resp = await get_poi_info(req, resp, osm_id)

    if resp.status_code == 504 or resp.status_code == 404:
        return
    else:
        resp.status_code = r.status_code

    data = json.loads(r.text)["hits"]["hits"][0]["_source"]
    # compose vcard
    begin = "BEGIN:VCARD\n"
    end = "END:VCARD"
    name = data["name"]
    lon, lat = data["location"]
    contact_email = data["labels"].get("contact_email", "")
    contact_fax = data["labels"].get("contact_fax", "")
    contact_phone = data["labels"].get("phone", "").replace(" ", "")
    contact_website = data["labels"].get("website", "")
    addr_street = data["labels"].get("addr_street", "")
    addr_housenumber = data["labels"].get("addr_housenumber", "")
    addr_postcode = data["labels"].get("addr_postcode", "")
    addr_city = data["labels"].get("addr_city", "")
    addr_country = data["labels"].get("addr_country", "")

    version = "VERSION:3.0"

    n = f"N:{name};;;;"
    fn = f"FN:{name}"
    address = (
        (
            f"ADR;TYPE=WORK:;;{addr_street} {addr_housenumber};"
            f"{addr_city};;{addr_postcode};{addr_country}\n"
        )
        if not data["labels"].get("address_incomplete")
        else ""
    )
    # v3
    # label = (
    #     f"LABEL;TYPE=WORK:{addr_street} {addr_housenumber},\n"
    #     f"{addr_postcode}{addr_city}\n{addr_country}"
    # )
    email = f"EMAIL:{contact_email}"
    geo = f"GEO:{lat},{lon}"
    phone = f"TEL;TYPE=WORK,voice;VALUE=tel:{contact_phone}"
    fax = f"TEL;TYPE=WORK FAX;VALUE=tel:{contact_fax}"
    url = f"URL:{contact_website}"
    source = f"SOURCE:{API_URL}osmid/{osm_id}.vcard"

    resp.headers = {
        "Content-Type": "text/vcard",
        "Content-disposition": 'attachment; filename="'
        + name.replace(" ", "_")
        + "_"
        + str(osm_id)
        + '.vcard"',
    }
    resp.text = (
        f"{begin}{version}\n{n}\n{fn}\n{address}{geo}\n{phone}\n{fax}\n"
        + f"{url}\n{email}\n{source}\n{end}"
    )


@api.route("/api/get_json/{osm_id}")  # legacy
async def get_json_old(req, resp, *, osm_id):
    """legacy function: get Info for osmID
    (use /api/osmid/{osm_id} instead)
    """
    return await get_json(req, resp, osm_id=osm_id)


@api.route("/api/osmid/{osm_id}")
async def get_json(req, resp, *, osm_id):
    """Get a vcard download for the given osm_id
    ---
    get:
        summary: get osm_id info
        description: returns info for the given `osm_id`
        responses:
            '200':
                description: OK
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/POI'
            '404':
                description: osm_id not found
            '504':
                description: could not connect to database
        parameters:
        -   name: osm_id
            in: path
            description: osmID, same as on OpenStreetMap.
            required: true
            schema:
                type: integer
            example: 317335810
    """
    r, resp = await get_poi_info(req, resp, osm_id)

    if resp.status_code == 504 or resp.status_code == 404:
        return
    else:
        resp.status_code = r.status_code

    data = json.loads(r.text)["hits"]["hits"][0]["_source"]
    if int(req.params.get("pretty", ["0"])[0]) == 1:
        resp.text = json.dumps(data, indent=4, sort_keys=True)
    else:
        resp.media = data


def _locate_user_ip(req):
    """locate the user's IP"""
    logger.info("client: " + str(req._starlette.client[0]))
    geoip = geoip2.database.Reader("./lib/geoip/GeoLite2-City.mmdb")

    # redirect users outside of DACH to
    fallback_lat, fallback_lon = 47.07070, 15.43950  # Graz
    # fallback_lat, fallback_lon = 49.4129, 8.6941 # Heidelberg, SOTM 2019

    client = str(req._starlette.client[0])
    forw_for = (
        req.headers["x-forwarded-for"] if "x-forwarded-for" in req.headers else client
    )
    remote_client = forw_for.split(",")[0]
    try:
        geoip_resp = geoip.city(remote_client)
        lat, lon = geoip_resp.location.latitude, geoip_resp.location.longitude
        if geoip_resp.country.iso_code not in ["AT", "DE", "CH", "LI"]:
            lat, lon = fallback_lat, fallback_lon
    except geoip2.errors.AddressNotFoundError:
        lat, lon = fallback_lat, fallback_lon
    geoip.close()

    data = {"ip": str(remote_client), "lat": lat, "lon": lon}
    return data


@api.route("/api/forward_ip")
async def locate_user_ip(req, resp):
    """forward user based on client IP"""
    data = _locate_user_ip(req)

    redir_url = SHORT_URL_REDIRECT_URL.format(zoom=13, x=data["lat"], y=data["lon"])
    logger.debug("redirect to --> %s", redir_url)
    resp.status_code = 302
    resp.headers["Location"] = redir_url


@api.route("/api/search/{query}")
async def simple_query_elastic_search(req, resp, *, query):
    """search YellowOSM for POIs (points of interest) aka businesses.
    ---
    get:
        summary: get search results
        description: Get POIs that match `query`
        responses:
            200:
                description: POIs returned.
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/POI'
        parameters:
        -   name: query
            in: path
            required: true
            schema:
                type: string
            example: Scherbe Graz
    """
    return await query_elastic_search(req, resp, query=query)


@api.route("/api/search/{city}/{query}")
async def city_query_elastic_search(req, resp, *, query, city):
    """search YellowOSM for POIs (points of interest) aka businesses.
    ---
    get:
        summary: get search results
        description: Get POIs that match `query`
        responses:
            200:
                description: POIs returned.
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/POI'
        parameters:
        -   name: query
            in: path
            required: true
            schema:
                type: string
            example: Weikhard
        -   name: city
            in: path
            description: limit search to 'city'
            required: true
            schema:
                type: string
            example: Graz
    """
    return await query_elastic_search(req, resp, query=query, city=city)


@api.route("/api/search/{city}/{query}/{limit}")
async def city_limit_query_elastic_search(req, resp, *, query, city, limit):
    """search YellowOSM for POIs (points of interest) aka businesses.
    ---
    get:
        summary: get search results
        description: |
            Get POIs that match `query`. search is limited to 'limit' number of results.
        responses:
            200:
                description: POIs returned.
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/POI'
        parameters:
        -   name: query
            in: path
            required: true
            schema:
                type: string
            example: Sacher
        -   name: city
            in: path
            description: limit search to 'city'
            required: true
            schema:
                type: string
            example: Wien
        -   name: limit
            in: path
            description: limit number of results to 'limit'
            required: true
            schema:
                type: integer
            example: 10
    """
    return await query_elastic_search(req, resp, query=query, city=city, limit=limit)


@api.route(
    "/api/search/"
    "{top_left_lat}/{top_left_lon}/{bottom_right_lat}/{bottom_right_lon}/{query}"
)
async def query_elastic_search(
    req,
    resp,
    *,
    query,
    city=None,
    limit=10000,
    top_left_lat=None,
    top_left_lon=None,
    bottom_right_lat=None,
    bottom_right_lon=None,
):

    """search YellowOSM for POIs (points of interest) aka businesses.
    ---
    get:
        summary: get search results
        description: |
            Get POIs that match `query`. search is limited to bounding-box coordinates.
        responses:
            200:
                description: POIs returned.
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/POI'
        parameters:
        -   name: query
            in: path
            required: true
            schema:
                type: string
            example: Tribeka
        -   name: top_left_lat
            in: path
            description: top left latitude of bounding-box
            required: true
            schema:
                type: number
            example: 47.09086
        -   name: top_left_lon
            in: path
            description: top left longitude of bounding-box
            required: true
            schema:
                type: number
            example: 15.39598
        -   name: bottom_right_lat
            in: path
            description: bottom right latitude of bounding-box
            required: true
            schema:
                type: number
            example: 47.03602
        -   name: bottom_right_lon
            in: path
            description: bottom right longitude of bounding-box
            required: true
            schema:
                type: number
            example: 15.48806
    """
    # ES_URL and ES_INDEX from settings env
    url = ES_URL + "/" + ES_INDEX + "/_search"
    logger.info("es index: " + ES_INDEX)
    es_filter = None
    es_query = None
    query = urllib.parse.unquote(str(query))

    if not top_left_lat:
        logger.debug("no bbox given .. falling back to DACH")
        # DACH region:
        tl_lat, tl_lon = 55.05918, 5.01902
        br_lat, br_lon = 45.98486, 17.25582
        es_filter = get_es_filter((tl_lat, tl_lon, br_lat, br_lon))
    else:
        tl_lat = float(top_left_lat)
        tl_lon = float(top_left_lon)
        br_lat = float(bottom_right_lat)
        br_lon = float(bottom_right_lon)
        logger.info(f"top_left_lat: {tl_lat}")
    if city:
        city = urllib.parse.unquote(str(city))
        if city.lower() in cities_bb.keys():
            tl_lat, tl_lon, br_lat, br_lon = cities_bb[city.lower()]["bb"]
            logger.debug(
                f"QUERY: {query} in {city} (boundingbox found: "
                "({}, {}, {}, {}))".format(tl_lat, tl_lon, br_lat, br_lon)
            )
            es_filter = get_es_filter((tl_lat, tl_lon, br_lat, br_lon))
            logger.debug(es_filter)
        else:
            logger.debug(f"QUERY: {query} in {city} (no bb found)")
            es_query = es_city_search(query, city, limit)

    logger.debug(f"QUERY: {query}")

    if not es_query:
        es_query = es_standard_search(query, es_filter, limit)

    logger.info(url)
    logger.info(es_query)
    r = requests.get(url, data=es_query, headers={"Content-Type": "application/json"})

    logger.info("status code: " + str(r.status_code))
    logger.info(r.text[:200])

    resp.status_code = r.status_code

    result = []
    for hit in json.loads(r.text)["hits"]["hits"]:
        loc = {
            "location": {
                "lat": hit["_source"]["location"][1],
                "lon": hit["_source"]["location"][0],
            }
        }
        result.append({**hit["_source"]["labels"], **loc})

    if result == []:
        resp.status_code = api.status_codes.HTTP_404
        resp.media = {"error": "Not Found"}
        logger.info(f"Nothing found: {query}")
    else:
        resp.media = result


if __name__ == "__main__":
    api.run(debug=DEBUG)
