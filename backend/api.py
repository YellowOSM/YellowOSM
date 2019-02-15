import time
import json

import responder

from lib import geo58

api = responder.API(cors=True)

@api.route("/api/")
@api.route("/api/hello")
def hello_world(req, resp):
    resp.text = "Hello World!"


@api.route("/api/hello/{user}")
@api.route("/api/hello/{user}/json")
def hello_json(req, resp, *, user):
    user = user.strip("/")
    resp.media = {"hello": user}

@api.route("/api/error")
def error(req, resp):
    resp.headers['X-Answer'] = '42'
    resp.status_code = 415
    resp.text = "ooops"

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

    resp.media = {'success': True}

@api.route("/api/coords_to_geo58/{zoom}/{x}/{y}")
async def convertCoordsToGeo58(req, resp, *, zoom, x, y):
    g58 = geo58.coordsToGeo58(zoom,x,y.strip('/ '))
    resp.media = {'g58': g58}

@api.route("/api/geo58_to_coords/{g58}")
async def convertCoordsToGeo58(req, resp, *, g58):
    zoom,x,y = geo58.geo58ToCoords(g58)
    resp.media = {'zoom': zoom,'x': x, 'y': y}

if __name__ == '__main__':
    api.run()
