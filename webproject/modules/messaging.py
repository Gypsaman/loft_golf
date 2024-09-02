from webproject.modules.loftemail import Email
from webproject.models import Players
from datetime import timedelta
from datetime import datetime as dt
from webproject.loft_app import db
from sqlalchemy import text
# from webproject.routes.requests import day_order

def submission_received(submission):
    day_order = ['Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','Monday']
    curr_week = submission.week
    player = Players.query.filter_by(id=submission.player_id).first()
    email = Email()
    body = f"Dear {player.first_name},\n\n"
    body += "Your tee time request has been received. You requested the following days "
    body += f"for the week of {curr_week.start_date.strftime('%B %d')} through {curr_week.end_date.strftime('%B %d')}:\n\n"
    for day in day_order:
        if getattr(submission,day):
            body += f"{day}\n"
    body += "\n\nYou will receive an email when your tee times are assigned.\n\n"
    email.send_email('gypsaman@gmail.com','Tee Time Request Received',body)

def tee_time_assigned(curr_week,category):
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

    body = f"Here are the tee times you requested, along with the other pairings "
    body += f"for {start_date.strftime('%b-%d')} to {(end_date - timedelta(days=1)).strftime('%b-%d')}:"

    curr_tee = None
    for teetime in teetimes:
        if curr_tee is None or curr_tee != teetime.time:
           body += "\n\n"+ dt.strptime(teetime.time[:-7],"%Y-%m-%d %H:%M:%S").strftime('%A %H:%M') + "\n"
           body += "===============\n"
           curr_tee = teetime.time
        
        body += f"{teetime.first_name} {teetime.last_name} \n"

    email = Email()
    for teetime in teetimes:
        email_body = f'{teetime.first_name},\n\n' + body
        email.send_email('gypsaman@gmail.com','Tee Time Assignment',email_body)
        break


def tee_time_added(tee_time,is_old,is_dup,requester):
    email = Email()
    body = f"A new tee time has been added for {tee_time.time.strftime('%A %b-%d %H:%M')}.\n"
    if is_old:
        body += "\nThis is for an older week than the current one. Please check the system."
    elif is_dup:
        body = f"A request to add {tee_time.time.strftime('%A %b-%d %H:%M')} has been received.\n\n This is a duplicate entry, No action taken."
    email.send_email(requester,'Tee Time Added',body)