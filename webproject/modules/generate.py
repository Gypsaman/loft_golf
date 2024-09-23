from webproject.models import Weeks
from datetime import timedelta
from webproject.models import TeeRequests, TeeTimePlayers, TeeTimes
from webproject.modules.extensions import db
from webproject.modules.utils import day_order, get_curr_week
from webproject.modules import messaging
from sqlalchemy import text



def generate(category):
    curr_week = get_curr_week()
    days_used = day_order[:4] if category == 'weekday' else day_order[4:]
    offset = 0 if category == 'weekday' else 4
    for idx,day in enumerate(days_used):
        start_date = curr_week.start_date + timedelta(days=idx+offset)
        end_date = curr_week.start_date + timedelta(days=idx+offset+1)
        tee_requests = [r.player_id for r in TeeRequests.query.filter(TeeRequests.week_id==curr_week.id,getattr(TeeRequests,day)==True).all()]
        guest_request =  [r.player_id for r in TeeRequests.query.filter(TeeRequests.week_id==curr_week.id,getattr(TeeRequests,day+'_guest')==True).all()]
        if len(tee_requests) == 0:
            continue
        while True:  # Randomly a group can become larger than 4 depending on the guests.  If so, try again.
            groups = group_requests(tee_requests,guest_request)
            if len([group for group in groups if len(group) > 4]) == 0:
                break
        tee_times = TeeTimes.query.filter(TeeTimes.week_id==curr_week.id,TeeTimes.time >= start_date, TeeTimes.time < end_date).order_by(TeeTimes.time).all()
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

def group_requests(players,guests):
    import random
    player_groups = {
        12:[4,4,4],
        11:[3,4,4],
        10:[2,4,4],
        9:[3,3,3],
        8:[4,4],
        7:[3,4],
        6:[3,3],
        5:[2,3],
    }

    num_players = len(players)+len(guests)
    if num_players < 5:
        return [players+guests]
    groups = []
    for qty in player_groups[num_players]:
        group = random.sample(players,qty if qty < len(players) else len(players))
        group = check_guests(group,guests,qty)
        groups.append(group)
        for player in group:
            if player in players:
                players.remove(player)

    return groups

def check_guests(group,guests,group_len):
    result = []
    for guest in guests:
        if guest in group:
            result.append(guest)
            result.append(guest)
            group.remove(guest)
        if len(result) == group_len:
            return result
    for player in group:
        if len(result) >= group_len:
            break
        result.append(player)
    
    return result
            
def is_player_booked(player,tee_time):
    start_date = tee_time.time.replace(hour=0,minute=0,second=0)
    end_date = tee_time.time.replace(hour=23,minute=59,second=59)
    sql = "Select TeeTimePlayers.id from teetimeplayers"
    sql += " join teetimes on teetimeplayers.tee_time_id = teetimes.id "
    sql += f" where teetimeplayers.player_id = {player} and teetimes.time > '{start_date}' and teetimes.time < '{end_date}'"

    results = list(db.session.execute(text(sql)))

    return len(results) > 0
    
