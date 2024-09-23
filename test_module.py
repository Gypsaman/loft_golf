from webproject.loft_app import app, db
from sqlalchemy import text
# from webproject.models import Players, User, Weeks, TeeTimes, TeeRequests
from webproject.modules.utils import get_curr_week
# import hashlib
# from werkzeug.security import generate_password_hash
# from datetime import datetime as dt
from webproject.modules.loft_processing import sleep_until_midnight, loft_process
from webproject.modules import messaging


with app.app_context():
    messaging.tee_times_available(get_curr_week(),'weekend')