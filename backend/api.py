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

if __name__ == '__main__':
    api.run()
