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


with app.app_context():
    category = 'weekend'
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    # offset = 0 if category == 'weekday' else 4
    # days_used = day_order[:4] if category == 'weekday' else day_order[4:]
    # for idx,day in enumerate(days_used):
    #     start_date = curr_week.start_date + timedelta(days=idx+offset)
    #     end_date = curr_week.start_date + timedelta(days=idx+offset+1)
    #     tee_requests = [r.player_id for r in TeeRequests.query.filter(TeeRequests.week_id==curr_week.id,getattr(TeeRequests,day)==True).all()]
    #     if len(tee_requests) == 0:
    #         continue
    #     groups = group_requests(tee_requests)
    #     tee_times = TeeTimes.query.filter(TeeTimes.week_id==curr_week.id,TeeTimes.time >= start_date, TeeTimes.time < end_date).all()
    #     for idx,tee_time in enumerate(tee_times):
    #         if idx >= len(groups):
    #             break
    #         group = groups[idx]
    #         for player in group:
    #             if is_player_booked(player,tee_time):
    #                 continue
    #             tee_time_player = TeeTimePlayers(player_id=player,tee_time_id=tee_time.id)
    #             db.session.add(tee_time_player)
    #     db.session.commit()
    messaging.tee_time_assigned(curr_week,category)

