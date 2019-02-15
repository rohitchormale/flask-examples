"""
flask-security-example.py

Requirements:
 Babel==2.6.0
 blinker==1.4
 Click==7.0
 Flask==1.0.2
 Flask-BabelEx==0.9.3
 Flask-Login==0.4.1
 Flask-Mail==0.9.1
 Flask-Principal==0.4.0
 Flask-Security==3.0.0
 Flask-SQLAlchemy==2.3.2
 Flask-WTF==0.14.2
 itsdangerous==1.1.0
 Jinja2==2.10
 MarkupSafe==1.1.0
 passlib==1.7.1
 pytz==2018.9
 speaklater==1.3
 SQLAlchemy==1.2.17
 Werkzeug==0.14.1
 WTForms==2.2.1

Usage:
 Run script using 'python flask-security-example.py'
 Visit below urls
    - url without login protection 'http://127.0.0.1:5000/marketing'
    - url with login protection 'http://127.0.0.1:5000/home'

References:
 - https://pythonhosted.org/Flask-Security/
 - https://pythonhosted.org/Flask-Mail/
"""
from flask import Flask

# flask-security
from flask_security import Security, RoleMixin, UserMixin, login_required
security = Security()

# flask-mail
from flask_mail import Mail
mail = Mail()

# database setup
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


##################
# database models
##################

from sqlalchemy.sql import func
roles_users = db.Table("roles_users",
                       db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
                       db.Column("role_id", db.Integer(), db.ForeignKey("role.id")))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, server_default=func.now())
    date_modified = db.Column(db.DateTime, onupdate=func.now())
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, server_default=func.now())
    date_modified = db.Column(db.DateTime, onupdate=func.now())
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))


####################
# customized forms
####################

from flask_security.forms import RegisterForm, ConfirmRegisterForm
from wtforms import StringField
from wtforms.validators import InputRequired, ValidationError, Length


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=32)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=32)])


class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=32)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=32)])


################################################################################################
# configuration (Do NOT commit passwords/secrets. See skeleton example to handle them securely)
################################################################################################

class Config(object):
    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = "sqlite:///temp.sqlite3"
    SECRET_KEY = "<my-secret-key>"
    # flask-security
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "<my-random-hash>"
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_CHANGABLE = True
    SECURITY_RECOVERABLE = True
    # flask-mail - if using gmail, make sure to enable access for less secure apps, from google security settings
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""


#######################
# application factory
#######################

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mail.init_app(app)
    from flask_security import SQLAlchemyUserDatastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore, register_form=ExtendedRegisterForm, confirm_register_form=ExtendedConfirmRegisterForm)
    db.init_app(app)

    with app.app_context():
        db.create_all()

        @app.route("/home")
        @login_required
        def home():
            return "<h3> Secured Sweet Home where no worries !!!! <h3>"

        @app.route("/marketing")
        def test():
            return "<h3> Marketing page open to all <h3>"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
