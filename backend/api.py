import time
import json
import logging
import os
import urllib.parse

import requests
import responder
from dotenv import load_dotenv
import geoip2.database

from lib.geo58 import Geo58

# import lib.es_queries
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
DEFAULT_ZOOM_LEVEL = os.getenv("DEFAULT_ZOOM_LEVEL", default=19)
ES_URL = os.getenv("ES_URL")
ES_INDEX = os.getenv("ES_INDEX", default="yosm")

api = responder.API(
    debug=DEBUG,
    version="0.2b",
    cors=True,
    cors_params={
        "allow_origins": ["*"],
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    },
)


logger.info("debug: " + DEBUG)
if DEBUG:
    logger.setLevel("DEBUG")
logger.debug("short url: " + SHORT_URL_REDIRECT_URL)


@api.route("/api/")
@api.route("/api/hello")
def hello_world(req, resp):
    resp.text = "Hello World!"


@api.route("/api/expensive-task")
async def handle_task(req, resp):
    @api.background.task
    def process_data(data):
        """This can take some time"""
        print("starting background task...")
        time.sleep(5)
        print("finished background task...")

    # parse incoming data form-encoded
    # json and yaml automatically work
    try:
        data = await req.media()
    except json.decoder.JSONDecodeError:
        data = None
        pass

    process_data(data)

    resp.media = {"success": True}


@api.route("/api/coords_to_geo58/{zoom}/{x}/{y}")
async def convertCoordsToGeo58(req, resp, *, zoom, x, y):
    try:
        g58 = Geo58(zoom=zoom, lat=x, lon=y.strip(" /"))
    except Geo58.Geo58Exception as ex:
        logger.debug(
            "Error: coords_to_geo58: Not Acceptable: coordinates invalid. [%s]", ex
        )
        resp.status_code = 406
        resp.text = "Error: Not Acceptable: coordinates invalid. [{}]".format(ex)
        return
    resp.media = {"geo58": g58.get_geo58()}


@api.route("/api/geo58_to_coords/{geo58_str}")
async def convertGeo58ToCoords(req, resp, *, geo58_str):
    try:
        g58 = Geo58(g58=geo58_str)
    except Geo58.Geo58Exception as ex:
        logger.debug("Error: geo58_to_coords: invalid short code: %s", ex)
        resp.status_code = 400
        resp.text = "Error: Bad Request: invalid short code. [{}]".format(ex)
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
        resp.text = "error: could not connect to database."
        resp.status_code = 504
        logger.error(ex)
    if json.loads(r.text)["hits"]["total"]["value"] == 0:
        resp.status_code = 404
        resp.text = "error: no data found."
    return (r, resp)


@api.route("/api/get_vcard/{osm_id}")
async def get_vcard(req, resp, *, osm_id):
    r, resp = await get_poi_info(req, resp, osm_id)

    if resp.status_code == 504 or resp.status_code == 404:
        return
    else:
        resp.status_code = r.status_code

    data = json.loads(r.text)["hits"]["hits"][0]["_source"]
    # compose vcard
    begin = "BEGIN:VCARD"
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
    # version = "VERSION:4.0"

    n = f"N:{name};;;;"
    fn = f"FN:{name}"
    # profile = "PROFILE:VCARD"
    # TODO if address incomplete omit address
    address = (
        f"ADR;TYPE=WORK:;;{addr_street} {addr_housenumber};"
        f"{addr_city};;{addr_postcode};{addr_country}"
    )
    # v3
    # label = (
    #     f"LABEL;TYPE=WORK:{addr_street} {addr_housenumber},\n"
    #     f"{addr_postcode}{addr_city}\n{addr_country}"
    # )
    email = f"EMAIL:{contact_email}"
    # v3
    geo = f"GEO:{lat},{lon}"
    # v4
    # geo = f"GEO:geo: {lat}\,{lon}"
    # v3
    phone = f"TEL;TYPE=WORK,voice;VALUE=tel:{contact_phone}"
    # v4
    # phone = f"TEL;TYPE=work,voice;VALUE=uri:tel:\"{contact_phone}\""
    # logger.debug(contact_phone)
    # v3
    fax = f"TEL;TYPE=WORK FAX;VALUE=tel:{contact_fax}"
    # v4
    # fax = f"TEL;TYPE=WORK FAX;VALUE=uri:tel:{contact_fax}"
    url = f"URL:{contact_website}"
    source = f"SOURCE:https://yellowosm.com/api/get_vcard/{osm_id}"

    resp.headers = {
        "Content-Type": "text/vcard",
        "Content-disposition": 'attachment; filename="'
        + name.replace(" ", "_")
        + "_"
        + str(osm_id)
        + '.vcard"',
    }
    resp.text = (
        f"{begin}\n{version}\n{n}\n{fn}\n{address}\n{geo}\n{phone}\n{fax}\n"
        + f"{url}\n{email}\n{source}\n{end}"
    )


@api.route("/api/get_json/{osm_id}")
async def get_json(req, resp, *, osm_id):
    r, resp = await get_poi_info(req, resp, osm_id)

    # logger.info(r.status_code)
    # logger.info(r.text)
    # logger.info(resp.status_code)
    # logger.info(resp.text)

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
    data = _locate_user_ip(req)

    redir_url = SHORT_URL_REDIRECT_URL.format(zoom=13, x=data["lat"], y=data["lon"])
    logger.debug("redirect to --> %s", redir_url)
    resp.status_code = 302
    resp.headers["Location"] = redir_url


@api.route("/api/search/{query}")
@api.route(
    "/api/search/{top_left_lat}/"
    "{top_left_lon}/{bottom_right_lat}/{bottom_right_lon}/{query}"
)
@api.route("/api/search/{city}/{query}")
async def query_elastic_search(
    req,
    resp,
    *,
    query,
    city=None,
    top_left_lat=None,
    top_left_lon=None,
    bottom_right_lat=None,
    bottom_right_lon=None,
):

    """search elastic search index for 'query'.
    add top left and bottom right coordinates to limit the results to
    geo-coordinates
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
                f"QUERY: {query} in {city} (boundingbox found)"
                "{}{}{}{}".format(tl_lat, tl_lon, br_lat, br_lon)
            )
            es_filter = get_es_filter((tl_lat, tl_lon, br_lat, br_lon))
            logger.debug(es_filter)
        else:
            logger.debug(f"QUERY: {query} in {city} (no bb found)")
            es_query = es_city_search(query, city)

    logger.debug(f"QUERY: {query}")

    if not es_query:
        es_query = es_standard_search(query, es_filter)

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


# @api.route("/api/cities_bb")
# async def query_elastic_search(req, resp):
#     resp.media = cities_bb


if __name__ == "__main__":
    api.run(debug=DEBUG)
