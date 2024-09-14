from webproject.models import Weeks


day_order = ['Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','Monday']

def get_curr_week():
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    if curr_week:
        return curr_week
    curr_week = Weeks.query.filter(Weeks.closed==True).order_by(Weeks.start_date.desc()).first()
    return curr_week

def generate(category):
    curr_week = get_curr_week()
    days_used = day_order[:4] if category == 'weekday' else day_order[4:]
    offset = 0 if category == 'weekday' else 4
    for idx,day in enumerate(days_used):
        start_date = curr_week.start_date + timedelta(days=idx+offset)
        end_date = curr_week.start_date + timedelta(days=idx+offset+1)
        while True:  # Randomly a group can become larger than 4 depending on the guests.  If so, try again.
            tee_requests = [r.player_id for r in TeeRequests.query.filter(TeeRequests.week_id==curr_week.id,getattr(TeeRequests,day)==True).all()]
            guest_request =  [r.player_id for r in TeeRequests.query.filter(TeeRequests.week_id==curr_week.id,getattr(TeeRequests,day+'_guest')==True).all()]
            if len(tee_requests) == 0:
                continue
            groups = group_requests(tee_requests,guest_request)
            if len([group for group in groups if len(group) > 4]) == 0:
                break
        tee_times = TeeTimes.query.filter(TeeTimes.week_id==curr_week.id,TeeTimes.time >= start_date, TeeTimes.time < end_date).all()
        for idx,tee_time in enumerate(tee_times):
            if idx >= len(groups):
                break
            group = groups[idx]
            for player in group:
                if is_player_booked(player,tee_time):
                    continue
                tee_time_player = TeeTimePlayers(player_id=player,tee_time_id=tee_time.id)
                db.session.add(tee_time_player)
        db.session.commit()
    messaging.tee_time_assigned(curr_week,category)