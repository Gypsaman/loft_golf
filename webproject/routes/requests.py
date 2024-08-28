from flask import Blueprint, redirect, render_template,  request, url_for, flash
from flask_login import login_required
from webproject.modules.extensions import db
from webproject.models import TeeTimes, Weeks, Players, TeeRequests, TeeTimePlayers
from datetime import datetime as dt
from datetime import timedelta
from collections import Counter
from sqlalchemy import func
from webproject.modules.table_creator import Field, TableCreator, true_false, time_to_day_time


requests = Blueprint('requests', __name__)

day_order = ['Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','Monday']

@requests.route('/requests/<access_code>')
def player_request(access_code):
    player = Players.query.filter_by(access_code=access_code).first()
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    teetimes = TeeTimes.query.filter_by(week_id=curr_week.id).all()
    days_available = Counter([dt.strftime(teetime.time,"%A") for teetime in teetimes])
    holidays = {teetime.time.strftime("%A"):teetime.holiday for teetime in teetimes}
    days_commited = get_committed_requests(curr_week.id)
    days = {}
    for idx,day in enumerate(day_order):
        if day in days_available:
            if days_commited[idx] <= days_available[day]*4:
                if holidays.get(day):
                    days[day] = days_available[day]*4 - days_commited[idx]
                    continue
                if idx < 5 and player.weekday:
                    days[day] = days_available[day]*4 - days_commited[idx]
                    continue
                if idx >= 5 and player.weekend:
                    days[day] = days_available[day]*4 - days_commited[idx]

    new = False
    request = TeeRequests.query.filter_by(player_id=player.id, week_id=curr_week.id).first()

    if not request:
        request = TeeRequests(player_id=player.id, week_id=curr_week.id,Monday=False, Tuesday=False, Wednesday=False, Thursday=False, Friday=False, Saturday=False, Sunday=False)
        db.session.add(request)
        db.session.commit()
        new = True
    
    return render_template("requests/player_request.html", 
                           player=player,days=days,curr_week=curr_week,request=request,new=new)

@requests.route('/requests/update/<int:id>', methods=['GET'])
@login_required
def update_request(id):
    tee_request = TeeRequests.query.filter_by(id=id).first()
    player = Players.query.filter_by(id=tee_request.player_id).first()
    return redirect(url_for('requests.player_request',access_code=player.access_code))

@requests.route('/requests/update/<int:id>', methods=['POST'])
def update_request_post(id):
    tee_request = TeeRequests.query.filter_by(id=id).first()
    tee_request.Monday = True if request.form.get('monday') else False
    tee_request.Tuesday = True if request.form.get('tuesday') else False
    tee_request.Wednesday = True if request.form.get('wednesday') else False
    tee_request.Thursday = True if request.form.get('thursday') else False
    tee_request.Friday = True if request.form.get('friday') else False
    tee_request.Saturday = True if request.form.get('saturday') else False
    tee_request.Sunday = True if request.form.get('sunday') else False
    db.session.commit()
    return redirect(url_for('requests.thank_you'))

@requests.route('/requests/thank_you')
def thank_you():
    return render_template("requests/thank_you.html")


@requests.route('/requests/generate/<category>')
@login_required
def generate_requests(category):
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    days_used = day_order[:4] if category == 'weekday' else day_order[4:]
    for idx,day in enumerate(days_used):
        start_date = curr_week.start_date + timedelta(days=idx)
        end_date = curr_week.start_date + timedelta(days=idx+1)
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
    return redirect(url_for('teetimes.pairings',page=1))


@requests.route('/requests')
@login_required
def view_requests():
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    fields = {
        'teerequests.id': Field(None,None),
        'players.first_name': Field(None,'First Name'),
        'players.last_name': Field(None,'Last Name'),
        'Monday': Field(true_false,'Monday'),
        'Tuesday': Field(true_false,'Tuesday'),
        'Wednesday': Field(true_false,'Wednesday'),
        'Thursday': Field(true_false,'Thursday'),
        'Friday': Field(true_false,'Friday'),
        'Saturday': Field(true_false,'Saturday'),
        'Sunday': Field(true_false,'Sunday')
    }
    table_creator = TableCreator('TeeRequests', condition=f'week_id = {curr_week.id}'
                                ,fields=fields,actions=['Edit'])
    table_creator.domain = 'requests/'
    table_creator.join('Players', 'teerequests.player_id = players.id')
    table_creator.set_items_per_page(20)
    table_creator.create_view()
    table = table_creator.create(1)
    

    return render_template("requests/view_requests.html", table=table,curr_week=curr_week)


def get_committed_requests(week_id):
    result = db.session.query(
    func.sum(TeeRequests.Monday.cast(db.Integer)).label('Monday'),
    func.sum(TeeRequests.Tuesday.cast(db.Integer)).label('Tuesday'),
    func.sum(TeeRequests.Wednesday.cast(db.Integer)).label('Wednesday'),
    func.sum(TeeRequests.Thursday.cast(db.Integer)).label('Thursday'),
    func.sum(TeeRequests.Friday.cast(db.Integer)).label('Friday'),
    func.sum(TeeRequests.Saturday.cast(db.Integer)).label('Saturday'),
    func.sum(TeeRequests.Sunday.cast(db.Integer)).label('Sunday')
    ).filter(TeeRequests.week_id == week_id).all()

    return result[0]

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