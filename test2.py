# from webproject.modules.process_emails import process_emails
from webproject.loft_app import app
from webproject.modules.extensions import db
from webproject.models import Players, User, Weeks, TeeTimes, TeeRequests, TeeTimePlayers
# from collections import Counter
# from webproject.routes.requests import get_committed_requests, day_order, group_requests,is_player_booked
# from datetime import datetime as dt
# from datetime import timedelta
# from sqlalchemy import text
# from webproject.modules  import messaging 
# from webproject.modules.loftemail import Email
from webproject.modules.process_emails import process_emails
from webproject.modules.utils import get_curr_week
from webproject.modules import messaging
from webproject.modules.generate import generate


with app.app_context():

   for t in TeeTimePlayers.query.all():
        db.session.delete(t)
   db.session.commit()
   generate('weekday')


