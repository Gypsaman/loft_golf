from webproject.modules.process_emails import process_emails
from webproject.loft_app import app, db
from webproject.models import Players, User, Weeks, TeeTimes, TeeRequests, TeeTimePlayers
from collections import Counter
from webproject.routes.requests import get_committed_requests, day_order, group_requests,is_player_booked
from datetime import datetime as dt
from datetime import timedelta
from sqlalchemy import text
from webproject.modules.messaging import tee_time_table


with app.app_context():
    category = 'weekday'
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()

    start = 0 if category == 'weekday' else 5
    end = 3 if category == 'weekday' else 7
    start_date = curr_week.start_date  + timedelta(days=start)
    end_date = curr_week.start_date + timedelta(days=end)


    sql = "Select players.first_name, players.last_name, players.email, teetimes.time from teetimeplayers"
    sql += " join players on teetimeplayers.player_id = players.id "
    sql += " join teetimes on teetimeplayers.tee_time_id = teetimes.id "
    sql += f" where teetimes.time >= '{start_date}' and teetimes.time < '{end_date}'"
    sql += " order by teetimes.time"

    teetimes = list(db.session.execute(text(sql)))

    tee_time_table(teetimes)
    