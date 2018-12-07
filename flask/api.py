from flask import Flask

from flask_openid import OpenID

from my_env import MY_VAR

app = Flask(__name__)

oid = OpenID(app, safe_roots=[])
print(fs_store_path)
print(dir(oid))
@app.route('/')
def hello_world():
    return 'Hello, World! ' + MY_VAR

# TODO write app
