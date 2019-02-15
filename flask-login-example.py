"""
flask-login-example.py

Requirements:
 Click==7.0
 Flask==1.0.2
 Flask-Login==0.4.1
 Flask-SQLAlchemy==2.3.2
 Flask-WTF==0.14.2
 itsdangerous==1.1.0
 Jinja2==2.10
 MarkupSafe==1.1.0
 SQLAlchemy==1.2.17
 Werkzeug==0.14.1
 WTForms==2.2.1

Usage:
 Run script using 'python flask-login-example.py'
 Visit below urls
    - url without login protection 'http://127.0.0.1:5000/marketing'
    - url with login protection 'http://127.0.0.1:5000/home'
    - On home page, login will be asked. Register yourself and then try to access again.

Notes:
    - In this example, we are not sending confirmation mail. This is a minimal example.
    - Also for proper folder structure you can use - https://github.com/rohitchormale/cookiecutter-flask

References:
 - https://flask-login.readthedocs.io/en/latest/
"""

from flask import Flask, redirect, render_template, render_template_string, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash

# flask-sqlalchemy setup
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# flask-login setup
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
login_manager = LoginManager()

# csrf setup
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()


##################
# database models
##################

from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, server_default=func.now())
    date_modified = db.Column(db.DateTime, onupdate=func.now())
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))



####################
# login forms
####################

from flask_wtf.form import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, Length, InputRequired, ValidationError


class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=32)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=32)])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=5, max=32)])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=5, max=32)])


####################
# Sample templates
###################

register_template = """
<form method="post" action="{{ url_for('register') }}">
    {{ form.csrf_token }}
  <h1>Sign up</h1>
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        {% for message in messages %}
                {{ message }}
        {% endfor %}
        {% endif %}
        {% endwith %}

    <p><input type="text"  name="first_name" placeholder="First Name" required autofocus></p>
    <p><input type="text" name="last_name" placeholder="Last Name" required autofocus></p>
    <p><input type="text" name="email" placeholder="email" required autofocus></p>
    <p><input type="password" name="password" placeholder="password" required></p>
    <p><button type="submit">Register</button></p>
    <p><a href="{{ url_for('login') }}">Already have account ?</a></p>
</form>
"""

login_template = """
<form method="post" action="{{ url_for('login') }}">
    {{ form.csrf_token }}
        <h1> Login </h1>
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        {% for message in messages %}
           {{ message }}
        {% endfor %}
        {% endif %}
        {% endwith %}

    <p><input type="text" name="email" placeholder="email" required autofocus></p>
    <p><input type="password" name="password" placeholder="password" required></p>
    <p><button class="btn btn-lg btn-primary btn-block" type="submit">Sign in</button></p>
    <p><a href="{{ url_for('register') }}">Not registered ?</a></p>
</form>
"""

home_template = """
<h3> Secured Sweet Home where no worries !!!! <h3>
<p><a href="{{ url_for('logout') }}">Logout</a></p>
"""


##########
# Helpers
##########

from flask import flash
def flash_errors(form):
    """Generate flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')


################################################################################################
# configuration (Do NOT commit passwords/secrets. See skeleton example to handle them securely)
################################################################################################

class Config(object):
    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = "sqlite:///temp.sqlite3"
    SECRET_KEY = "<my-secret-key>"


#######################
# application factory
#######################

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # initialize extensions
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    db.init_app(app)


    with app.app_context():
        db.create_all()

        ##############
        # Controllers
        ##############

        @login_manager.user_loader
        def load_user(id):
            return User.query.get(int(id))


        @app.route("/register", endpoint="register", methods=["GET", "POST"])
        def register():
            """Handle register request"""
            if current_user.is_authenticated:
                return redirect(url_for('home'))
            form = RegisterForm(request.form)
            if request.method == "POST" and form.validate_on_submit():
                password = generate_password_hash(form.password.data, method="sha256")
                user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,
                            password=password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                app.logger.info("New user registered successfully using form | %s" % user.email)
                return redirect(url_for("home"))
            else:
                app.logger.error("New user registration using form failed")
                flash_errors(form)
            # return render_template("register.html", form=form)
            return render_template_string(register_template, form=form)


        @app.route("/login", endpoint="login", methods=["GET", "POST"])
        def login():
            """Handle login request."""
            if current_user.is_authenticated:
                return redirect(url_for("home"))
            form = LoginForm(request.form)
            if request.method == "POST" and form.validate():
                user = User.query.filter_by(username=form.username.data).first()
                if user is None or not check_password_hash(user.password, form.password.data):
                    flash("Invalid username/password")
                    return render_template("login.html", form=form)
                login_user(user)
                app.logger.debug("User login successful | %s" % user.username)
                return redirect(url_for("home"))
            else:
                flash_errors(form)
                app.logger.debug("User login failed")
            # return render_template("login.html", form=form)
            return render_template_string(login_template, form=form)


        @app.route("/logout", endpoint="logout")
        @login_required
        def logout():
            """Handle logout request"""
            logout_user()
            return redirect(url_for("login"))


        @app.route("/home", endpoint="home")
        @app.route("/")
        @login_required
        def home():
            """Home page view. Protected view"""
            return render_template_string(home_template)


        @app.route("/marketing", endpoint="marketing")
        def marketing():
            """Unprotected view"""
            return "<h3> This is marketing page </h3>"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
