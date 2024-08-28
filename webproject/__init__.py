from flask import Flask
from webproject.modules.extensions import db,migrate
from datetime import timedelta

def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loft.db'
    app.config['SECRET_KEY'] = 'LOFT'
    app.permanent_session_lifetime = timedelta(minutes=5)

    db.init_app(app)
    migrate.init_app(app, db)

    from webproject.routes.main import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)\
    
    return app