"""
flask-admin-example.py

Requirements:
Click==7.0
Flask==1.0.2
Flask-Admin==1.5.3
Flask-SQLAlchemy==2.3.2
itsdangerous==1.1.0
Jinja2==2.10
MarkupSafe==1.1.0
SQLAlchemy==1.2.17
Werkzeug==0.14.1
WTForms==2.2.1

Usage:
 - Run script using 'python flask-admin-example.py'
 - Then visit 'http://127.0.0.1:5555/admin'

References:
- https://flask-admin.readthedocs.io/en/latest/

"""
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# database setup
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# database models
from sqlalchemy.sql import func
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, server_default=func.now())
    date_modified = db.Column(db.DateTime, onupdate=func.now())
    username = db.Column(db.String(32), nullable=False, unique=True)
    posts = db.relationship("Post", backref="user", lazy=True)

    def __repr__(self):
        return "<%s>" % self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, server_default=func.now())
    date_modified = db.Column(db.DateTime, onupdate=func.now())
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(32), nullable=False)
    text = db.Column(db.Text)

    def __repr__(self):
        return "<%s>" % self.title


def create_app():
    # init flask app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///temp.sqlite3"
    app.config["SECRET_KEY"] = "<my-secret-key>"
    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

    db.init_app(app)

    with app.app_context():
        # init admin
        admin = Admin(app, name="microblog", template_mode="bootstrap3")
        admin.add_view(ModelView(User, db.session))
        admin.add_view(ModelView(Post, db.session))

        # create tables
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
