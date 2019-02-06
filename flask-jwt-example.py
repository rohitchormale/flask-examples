"""
flask-jwt example

# Usage

- Run script 

python flask-jwt-example.py


- get jwt token

url: /api/auth/get_token
method: POST
body: {"username": <username>, "password": <password>}

- use token

Add 'authorization' header with value as 'JWT <auth-token>'
e.g.
url: /home
method: GET
headers: authorization: JWT 1313asfasdfsd13113assdf


# References:
- https://pythonhosted.org/Flask-JWT/

"""
from flask import Flask
from flask_jwt import JWT, jwt_required, current_identity


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id=%s)" % self.id

users = [
    User(1, 'user1', 'user1'),
    User(2, 'user2', 'user2'),
]

username_table = {u.username: u for u in users}
userid_table =  {u.id: u for u in users}

from werkzeug.security import safe_str_cmp
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)

class ConfigClass(object):
    JWT_AUTH_URL_RULE = "/api/auth/get_token"

app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "my-secret-key"
app.config.from_object(ConfigClass)
jwt = JWT(app, authenticate, identity)


@app.route("/home")
@jwt_required()
def home():
    return 'home'

if __name__ == "__main__":
    app.run()
