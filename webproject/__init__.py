from flask import Flask
from webproject.modules.extensions import db,migrate
from datetime import timedelta
from webproject import loft_app
def create_app():


    
    return loft_app.app