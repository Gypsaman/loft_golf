from webproject.loft_app import app, db
from webproject.models import Players, User, Weeks, TeeTimes, TeeRequests
import hashlib
from werkzeug.security import generate_password_hash
from datetime import datetime as dt


def add_players():
    with open('players.csv', 'r') as f:
        data = f.readlines()
    for player in data[1:]:
        player = player.strip().split(',')
        phone_number = player[5]
        phone_number = phone_number.replace('(', '')
        phone_number = phone_number.replace(')', '-')
        new_player = Players(
            first_name=player[0],
            last_name=player[1],
            weekday=True if player[2] == '1' else False,
            weekend=True if player[3] == '1' else False,
            email=player[4],
            ghin = '1234',
            handicap=0,
            phone=phone_number,
            access_code= hashlib.sha256(player[4].encode()).hexdigest()[:4],
            active = True
        )
        db.session.add(new_player)
    db.session.commit()

def add_users():
    user = User(
        email='ghoelscher@gmail.com',
        password=generate_password_hash('Mazzy',method='pbkdf2:sha256'),
        role='admin'
    )
    db.session.add(user)
    user = User(
        email='gypsaman@gmail.com',
        password=generate_password_hash('Bytor',method='pbkdf2:sha256'),
        role='admin'
    )
    db.session.add(user)
    db.session.commit()

def add_weeks():
    weeks = [
        Weeks(start_date=dt.strptime('2024-08-27',"%Y-%m-%d"), end_date=dt.strptime('2024-09-02',"%Y-%m-%d"), closed=True),
        Weeks(start_date=dt.strptime('2024-09-03',"%Y-%m-%d"), end_date=dt.strptime('2024-09-09',"%Y-%m-%d"), closed=True),
        Weeks(start_date=dt.strptime('2024-09-10',"%Y-%m-%d"), end_date=dt.strptime('2024-09-16',"%Y-%m-%d"), closed=False)
    ]
    for week in weeks:
        db.session.add(week)
    db.session.commit()
    db.session.refresh(week)
    add_tee_times(week)
    add_requests(week)

def add_requests(week):
    players = Players.query.limit(10)
    for player in players:
        monday = player.weekday
        tuesday = player.weekday
        wednesday = player.weekday
        thursday = player.weekday
        friday = player.weekday
        saturday = player.weekend
        sunday = player.weekend
        request = TeeRequests(player_id=player.id, week_id=week.id, Monday=monday, Tuesday=tuesday, Wednesday=wednesday, Thursday=thursday, Friday=friday, Saturday=saturday, Sunday=sunday)
        db.session.add(request)
    db.session.commit()

def add_tee_times(week):
    times = [dt.strptime('2024-09-16 08:10 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-16 08:20 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-16 08:30 am',"%Y-%m-%d %I:%M %p"),
             dt.strptime('2024-09-10 08:10 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-10 08:20 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-10 08:30 am',"%Y-%m-%d %I:%M %p"),
             dt.strptime('2024-09-11 08:10 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-11 08:20 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-11 08:30 am',"%Y-%m-%d %I:%M %p"),
             dt.strptime('2024-09-12 08:10 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-12 08:20 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-12 08:30 am',"%Y-%m-%d %I:%M %p"),
             dt.strptime('2024-09-14 08:10 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-14 08:20 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-14 08:30 am',"%Y-%m-%d %I:%M %p"),
             dt.strptime('2024-09-15 08:10 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-15 08:20 am',"%Y-%m-%d %I:%M %p"), 
             dt.strptime('2024-09-15 08:30 am',"%Y-%m-%d %I:%M %p")
             ]
    for time in times:
        tee_time = TeeTimes(week_id=week.id, time=time, closed=False, holiday=False)
        db.session.add(tee_time)
    db.session.commit()

with app.app_context():

    db.create_all()
    add_players()
    add_users()
    # add_weeks() 

    # for requests in TeeRequests.query.all():
    #     if not (requests.Monday or requests.Tuesday or requests.Wednesday or requests.Saturday):
    #         print(requests)
        # print(requests.Monday, requests.Tuesday, requests.Wednesday, requests.Saturday)

    # for week in Weeks.query.all():
    #     print(week)
    # for player in Players.query.all():
    #     if not (player.weekday or player.weekend):
    #         print(player)
        # print(player.weekday, player.weekend)

