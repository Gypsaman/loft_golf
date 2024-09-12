from webproject.modules.process_emails import process_emails
from webproject.loft_app import app, db
from webproject.models import Players, User, Weeks, TeeTimes, TeeRequests, TeeTimePlayers
from collections import Counter
from webproject.routes.requests import get_committed_requests, day_order, group_requests,is_player_booked
from datetime import datetime as dt
from datetime import timedelta
from sqlalchemy import text
from webproject.modules  import messaging 
from webproject.modules.loftemail import Email
from webproject.modules.process_emails import process_emails


with app.app_context():
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    messaging.tee_times_available(curr_week,'weekday')



