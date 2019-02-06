"""
This small script demonstrate example of JWT authentication using flask-jwt extension.
Most of code is copied from links in references.

Requirements:
Click==7.0
Flask==1.0.2
Flask-JWT==0.3.2
itsdangerous==1.1.0
Jinja2==2.10
MarkupSafe==1.1.0
PyJWT==1.4.2
Werkzeug==0.14.1


Usage:
To use flask-jwt, 2 functions needs to define
1. authenticate(username, password)
2. identity(payload)

To run script 'python flask-jwt-example.py'

To get jwt token send POST request to url '/api/auth/get_token' (configured in ConfigClass)
url: /api/auth/get_token
method: POST
body: {"username": <username>, "password": <password>}

To use JWT token, add 'authorization' header with token value along with prefix 'JWT'
e.g.
url: /home
method: GET
headers: authorization: JWT 1313asfasdfsd13113assdf


References:
- https://pythonhosted.org/Flask-JWT/

"""
from werkzeug.security import safe_str_cmp
from flask import Flask
from flask_jwt import JWT, jwt_required, current_identity


class User(object):
    """Example User class"""
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id=%s)" % self.id


# Instead of actual database, we are using here python variables to store data
users = [
    User(1, 'user1', 'user1'),
    User(2, 'user2', 'user2'),
]
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


# implementing required functions
def authenticate(username, password):
    """Authenticate user and return User instance based on username and password"""
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    """Return User instance or None based on token"""
    user_id = payload['identity']
    return userid_table.get(user_id, None)


class ConfigClass(object):
    """Test Configuration"""
    SECRET_KEY = "my-secret-key"
    JWT_AUTH_URL_RULE = "/api/auth/get_token"


# initialize app and JWT
app = Flask(__name__)
app.debug = True
app.config.from_object(ConfigClass)
jwt = JWT(app, authenticate, identity)


# protecting view
@app.route("/home")
@jwt_required()
def home():
    return 'home'


if __name__ == "__main__":
    app.run()
