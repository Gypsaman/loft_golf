from flask import Flask
from flask_login import LoginManager

from webproject.modules.extensions import db,migrate
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loft_golf.db'
app.config['SECRET_KEY'] = 'LOFT'
# app.permanent_session_lifetime = timedelta(minutes=5)

db.init_app(app)
migrate.init_app(app, db)


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

from webproject.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from webproject.routes.main import main as main_blueprint
app.register_blueprint(main_blueprint)

from webproject.routes.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from webproject.routes.players import players as players_blueprint
app.register_blueprint(players_blueprint)

from webproject.routes.weeks import weeks as weeks_blueprint
app.register_blueprint(weeks_blueprint)

from webproject.routes.teetimes import teetimes as teetimes_blueprint
app.register_blueprint(teetimes_blueprint)

from webproject.routes.requests import requests as requests_blueprint
app.register_blueprint(requests_blueprint)