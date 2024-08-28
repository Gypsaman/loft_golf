from webproject.models import Players
from sqlalchemy import func, text
from webproject.loft_app import app, db
from webproject.models import Weeks, TeeTimes, TeeRequests, TeeTimePlayers
from datetime import datetime as dt
from datetime import timedelta
from webproject.routes.requests import get_committed_requests
from collections import Counter
from webproject.modules.loftemail import Email



def group_requests(players):
    import random
    player_groups = {
        12:[4,4,4],
        11:[3,4,4],
        10:[2,4,4],
        9:[3,3,3],
        8:[2,3,3],
        7:[3,4],
        6:[3,3],
        5:[2,3],
    }

    num_players = len(players)
    if num_players < 5:
        return players
    groups = []
    for qty in player_groups[num_players][:-1]:
        group = random.sample(players,qty)
        groups.append(group)
        for player in group:
            players.remove(player)
    groups.append(players)

    return groups


with app.app_context():

    access_code = '69e1'
    day_order = ['Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','Monday']
    category = 'weekend'
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    days_used = day_order[:4] if category == 'weekday' else day_order[4:]
    offset = 0 if category == 'weekday' else 4
    for idx,day in enumerate(days_used):
        start_date = curr_week.start_date + timedelta(days=idx+offset)
        end_date = curr_week.start_date + timedelta(days=idx+1+offset)
        tee_requests = [r.player_id for r in TeeRequests.query.filter(TeeRequests.week_id==curr_week.id,getattr(TeeRequests,day)==True).all()]
        groups = group_requests(tee_requests)
        tee_times = TeeTimes.query.filter(TeeTimes.week_id==curr_week.id,TeeTimes.time >= start_date, TeeTimes.time < end_date).all()
        for idx,tee_time in enumerate(tee_times):
            if idx >= len(groups):
                break
            group = groups[idx]
            for player in group:
                tee_time_player = TeeTimePlayers(player_id=player,tee_time_id=tee_time.id)
                db.session.add(tee_time_player)
        db.session.commit()
    # player = Players.query.filter_by(access_code=access_code).first()
    # curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    # teetimes = TeeTimes.query.filter_by(week_id=curr_week.id).all()
    # holidays = {teetime.time.strftime("%A"):teetime.holiday for teetime in teetimes}
    # days_available = Counter([dt.strftime(teetime.time,"%A") for teetime in teetimes])
    # days_commited = get_committed_requests(curr_week.id)
    # days = {}
    # for idx,day in enumerate(day_order):
    #     if day in days_available:
    #         if days_commited[idx] <= days_available[day]*4:
    #             if idx < 5 and player.weekday:
    #                 days[day] = days_available[day]*4 - days_commited[idx]
    #             if idx >= 5 and player.weekend:
    #                 days[day] = days_available[day]*4 - days_commited[idx]
    # request = TeeRequests.query.filter_by(player_id=player.id, week_id=curr_week.id).first()
    # if not request:
    #     request = TeeRequests(player_id=player.id, week_id=curr_week.id,Monday=False, Tuesday=False, Wednesday=False, Thursday=False, Friday=False, Saturday=False, Sunday=False)
    #     db.session.add(request)
    #     db.session.commit()
    # print(request)
    # requests = TeeRequests.query.all()
    # for request in requests:
    #     print(request)




        # break

    # teetimes = [tee.id for tee in TeeTimes.query.filter_by(week_id=curr_week.id).all()]
    # groupings = TeeTimePlayers.query.filter(TeeTimePlayers.tee_time_id.in_(teetimes)).all()
    # for group in groupings:
    #     print(group.player_id, group.tee_time.time)
        

    # stmt = "select Players.first_name,Players.last_name, TeeTimes.time from teetimeplayers "
    # stmt += " inner join players on teetimeplayers.player_id=players.id "
    # stmt += " inner join teetimes on teetimeplayers.tee_time_id=teetimes.id"
    # stmt += f" where teetimes.week_id={curr_week.id}"
    # tees = list(db.session.execute(text(stmt)))

    # for tee in tees:
    #     print(tee)


# from webproject.modules.loftemail import Email

# email = Email()
# emails = email.receive_emails()
# print(emails)

