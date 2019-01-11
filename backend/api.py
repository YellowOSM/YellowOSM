import time
import json

import responder

api = responder.API()

@api.route("/")
@api.route("/hello")
def hello_world(req, resp):
    resp.text = "Hello World!"


@api.route("/hello/{user}")
def hello_user(req, resp, *, user):
    user = user.strip("/")
    resp.text = f"Hello, {user}!"

@api.route("/api/hello/{user}")
@api.route("/api/hello/{user}/json")
def hello_json(req, resp, *, user):
    user = user.strip("/")
    resp.media = {"hello": user}

@api.route("/error")
def error(req, resp):
    resp.headers['X-Answer'] = '42'
    resp.status_code = 415
    resp.text = "ooops"

@api.route("/expensive-task")
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


if __name__ == '__main__':
    api.run()
