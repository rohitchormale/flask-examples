"""

Requirements:
Click==7.0
Flask==1.0.2
Flask-JWT-Extended==3.17.0
itsdangerous==1.1.0
Jinja2==2.10
MarkupSafe==1.1.0
PyJWT==1.7.1
Werkzeug==0.14.1


Usage:
- Run script as 'python flask-jwt-extended-example.py'

- As per below implementation, to generate token, send POST request to '/api/auth/create_token' with username and password.
But flask-jwt-extended apis are well abstracted. So we can generate token using 'flask.current_user' too.

- To use token, add 'authorization' header with value 'Bearer <access_token>'

References:
- https://flask-jwt-extended.readthedocs.io/en/latest/

"""

import datetime
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from werkzeug.security import safe_str_cmp


class ConfigClass(object):
    """Test Configuration"""
    DEBUG = True
    JWT_SECRET_KEY = "my-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=30)


class User(object):
    """Example User class"""
    def __init__(self, id, username, password, roles):
        self.id = id
        self.username = username
        self.password = password
        self.roles = roles

    def __str__(self):
        return "User(id=%s)" % self.id


# Instead of actual database, we are using here python variables to store data
users = [
    User(1, 'user1', 'pass1', ["role1", "role2"]),
    User(2, 'user2', 'pass2', ["role3", "role4"]),
]
userid_table = {user.username: user for user in users}


app = Flask(__name__)
app.config.from_object(ConfigClass)
jwt = JWTManager(app)


@jwt.user_identity_loader
def load_api_user(user):
    """Generate tokens using specific attribute of object."""
    # If you see, docs of 'create_access_token' func, 'identity' can be anything but json serializable object.
    return user.username


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {"roles": user.roles}


@app.route("/api/auth/create_token", methods=["POST"])
def create_token():
    # Here, after authentication, u will get user object.( using login_required and current_user)
    # For test purpose, we are fetching from users
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = userid_table.get(username)
    current_user = users[0]
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        access_token = create_access_token(identity=current_user)
        return jsonify({"access_token": access_token}), 200
    return jsonify({"msg": "Invalid credentials"})


@app.route("/api/users", methods=["GET"])
@jwt_required
def list_users():
    current_user = get_jwt_identity()
    user_list = [user.username for user in users]
    return jsonify({"type": "+OK", "msg": "success", "users": user_list}), 200


if __name__ == "__main__":
    app.run()
