from webproject.modules.loftemail import Email
from datetime import datetime as dt
from datetime import timedelta
from webproject.models import TeeTimes, Weeks
from webproject.loft_app import db, app
from  webproject.modules import messaging


def process_emails():
    email = Email()

    emails_received = email.receive_emails()

    for email in emails_received:
        for content in email['content']:
            if content.startswith("BEGIN:VCALENDAR"):
                idx = content.find("START:")
                if not idx:
                    continue
                tee_time = dt.strptime(content[idx+6:idx+20],"%Y%m%dT%H%M%S")
                add_tee_time(tee_time,requester=email['from'])
                break
    
def add_tee_time(tee_time_request,requester='gypsaman@gmail.com'):

    curr_week = get_curr_week()
    start_date, end_date = get_week_start_end(tee_time_request)
    is_old = False if not curr_week else curr_week.start_date > start_date
    tee_week = Weeks.query.filter(Weeks.start_date == start_date).first()
    if tee_week is None:
        tee_week = Weeks(start_date=start_date, end_date=end_date, closed=False)
        db.session.add(tee_week)
        db.session.commit()
    teetime = TeeTimes.query.filter(TeeTimes.week_id == tee_week.id, TeeTimes.time == tee_time_request).first()
    is_dup = True if teetime else False
    if not is_dup:
        teetime = TeeTimes(week_id=tee_week.id, time=tee_time_request, holiday=False, closed=False)
        db.session.add(teetime)
        db.session.commit()
    messaging.tee_time_added(teetime, is_old, is_dup,requester)

            
def get_week_start_end(date):
    weekday = date.weekday()
    start_date = date - timedelta(days=(weekday-1)%7)
    end_date = start_date + timedelta(days=6)
    return start_date.replace(hour=0,minute=0,second=0), end_date.replace(hour=23,minute=59,second=59)

def get_curr_week():
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    if curr_week:
        return curr_week
    curr_week = Weeks.query.filter(Weeks.closed==True).order_by(Weeks.start_date.desc()).first()
    if curr_week:
        return curr_week
    return None

if __name__ == '__main__':
    with app.app_context():
        process_emails()