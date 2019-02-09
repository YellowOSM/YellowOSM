import time
import json

import responder

from lib import base58

api = responder.API()

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

@api.route("/api/coords_to_base58/{zoom}/{x}/{y}")
async def convertCoordsToBase58(req, resp, *, zoom, x, y):
    b58 = base58.coordsToBase58(zoom,x,y)
    resp.media = {'b58': b58}

@api.route("/api/base58_to_coords/{b58}")
async def convertCoordsToBase58(req, resp, *, b58):
    zoom,x,y = base58.base58ToCoords(b58)
    resp.media = {'zoom': zoom,'x': x, 'y': y}

if __name__ == '__main__':
    api.run()
