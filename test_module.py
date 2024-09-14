from webproject.loft_app import app, db
from webproject.models import Players, User, Weeks, TeeTimes, TeeRequests
from webproject.modules.utils import get_curr_week
import hashlib
from werkzeug.security import generate_password_hash
from datetime import datetime as dt


with app.app_context():
    curr_week = get_curr_week()
    curr_week.weekday_request = True
    curr_week.weekend_request = True
    db.session.commit()
    

