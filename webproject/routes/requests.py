from flask import Blueprint, redirect, render_template,  request, url_for, flash
from flask_login import login_required
from webproject.modules.extensions import db
from webproject.models import TeeTimes, Weeks, Players, TeeRequests, TeeTimePlayers
from datetime import datetime as dt
from datetime import timedelta
from collections import Counter
from sqlalchemy import func
from webproject.modules.table_creator import Field, TableCreator, true_false, time_to_day_time
from webproject.modules import messaging
from webproject.modules.utils import get_curr_week,day_order,generate
from sqlalchemy import text


requests = Blueprint('requests', __name__)



@requests.route('/requests/<category>/<access_code>')
def player_request(category,access_code):
    player = Players.query.filter_by(access_code=access_code).first()
    curr_week = get_curr_week()
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
                if idx < 4 and player.weekday:
                    days[day] = days_available[day]*4 - days_commited[idx]
                    continue
                if idx >= 4 and player.weekend:
                    days[day] = days_available[day]*4 - days_commited[idx]

    new = False
    request = TeeRequests.query.filter_by(player_id=player.id, week_id=curr_week.id).first()

    if not request:
        request = TeeRequests(player_id=player.id, week_id=curr_week.id,Monday=False, Tuesday=False, Wednesday=False, Thursday=False, Friday=False, Saturday=False, Sunday=False, Monday_guest=False, Tuesday_guest=False, Wednesday_guest=False, Thursday_guest=False, Friday_guest=False, Saturday_guest=False, Sunday_guest=False)
        db.session.add(request)
        db.session.commit()

    
    return render_template("requests/player_request.html", 
                           player=player,days=days,curr_week=curr_week,request=request,category=category)

@requests.route('/requests/update/<category>/<int:id>', methods=['GET'])
@login_required
def update_request(category,id):
    tee_request = TeeRequests.query.filter_by(id=id).first()
    player = Players.query.filter_by(id=tee_request.player_id).first()
    return redirect(url_for('requests.player_request',access_code=player.access_code))

@requests.route('/requests/update/<category>/<int:id>', methods=['POST'])
def update_request_post(category,id):
    tee_request = TeeRequests.query.filter_by(id=id).first()
    if category == 'weekday':
        tee_request.Tuesday = True if request.form.get('tuesday') else False
        tee_request.Wednesday = True if request.form.get('wednesday') else False
        tee_request.Thursday = True if request.form.get('thursday') else False
        tee_request.Friday = True if request.form.get('friday') else False
        tee_request.Tuesday_guest = True if request.form.get('tuesday_guest') else False
        tee_request.Wednesday_guest = True if request.form.get('wednesday_guest') else False
        tee_request.Thursday_guest = True if request.form.get('thursday_guest') else False
        tee_request.Friday_guest = True if request.form.get('friday_guest') else False
    if category == 'weekend':
        tee_request.Monday = True if request.form.get('monday') else False
        tee_request.Saturday = True if request.form.get('saturday') else False
        tee_request.Sunday = True if request.form.get('sunday') else False
        tee_request.Monday_guest = True if request.form.get('monday_guest') else False
        tee_request.Saturday_guest = True if request.form.get('saturday_guest') else False
        tee_request.Sunday_guest = True if request.form.get('sunday_guest') else False
    db.session.commit()
    messaging.submission_received(tee_request)
    return redirect(url_for('requests.thank_you'))

@requests.route('/requests/thank_you')
def thank_you():
    return render_template("requests/thank_you.html")


@requests.route('/requests/generate/<category>')
@login_required
def generate_requests(category):
    generate(category)
    
    return redirect(url_for('teetimes.pairings',page=1))

def is_player_booked(player,tee_time):
    start_date = tee_time.time.replace(hour=0,minute=0,second=0)
    end_date = tee_time.time.replace(hour=23,minute=59,second=59)
    sql = "Select TeeTimePlayers.id from teetimeplayers"
    sql += " join teetimes on teetimeplayers.tee_time_id = teetimes.id "
    sql += f" where teetimeplayers.player_id = {player} and teetimes.time > '{start_date}' and teetimes.time < '{end_date}'"

    results = list(db.session.execute(text(sql)))

    return len(results) > 0
    


@requests.route('/requests')
@login_required
def view_requests():
    curr_week = get_curr_week()
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
    func.sum(TeeRequests.Tuesday.cast(db.Integer) + TeeRequests.Tuesday_guest.cast(db.Integer)).label('Tuesday'),
    func.sum(TeeRequests.Wednesday.cast(db.Integer) + TeeRequests.Wednesday_guest.cast(db.Integer)).label('Wednesday'),
    func.sum(TeeRequests.Thursday.cast(db.Integer) + TeeRequests.Thursday_guest.cast(db.Integer)).label('Thursday'),
    func.sum(TeeRequests.Friday.cast(db.Integer) + TeeRequests.Friday_guest.cast(db.Integer)).label('Friday'),
    func.sum(TeeRequests.Saturday.cast(db.Integer) + TeeRequests.Saturday_guest.cast(db.Integer)).label('Saturday'),
    func.sum(TeeRequests.Sunday.cast(db.Integer) + TeeRequests.Sunday_guest.cast(db.Integer)).label('Sunday'),
    func.sum(TeeRequests.Monday.cast(db.Integer) + TeeRequests.Monday_guest.cast(db.Integer)).label('Monday')
    ).filter(TeeRequests.week_id == week_id).all()

    committed = []
    for r in result[0]:
        committed.append(r if r else 0)

    return committed

def group_requests(players,guests):
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
            