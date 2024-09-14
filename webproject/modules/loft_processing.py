from webproject.modules import messaging
from webproject.loft_app import app
from webproject.modules.extensions import db
from webproject.modules.utils import get_curr_week, generate, day_order
from datetime import datetime as dt
from datetime import timedelta
import time
import calendar
from webproject.models import Weeks
from webproject.modules.process_emails import process_emails



weekday_request = 'Friday'
weekday_teetime = 'Monday'
weekend_request = 'Saturday'
weekend_teetime = 'Wednesday'

def loft_process():
    with app.app_context():

        curr_week = get_curr_week()

        now = dt.today()

        process_emails()
            
        if not curr_week.weekday_request and calendar.day_name[now.weekday()] == weekday_request:
            messaging.tee_times_available(curr_week,'weekday')    
            curr_week.weekday_request = True
            db.session.commit()

        if not curr_week.weekend_request and  calendar.day_name[now.weekday()] == weekend_request:
            messaging.tee_times_available(curr_week,'weekend')
            curr_week.weekend_request = True
            db.session.commit()

        if not curr_week.weekday_teetimes and curr_week.weekday_request and  calendar.day_name[now.weekday()] == weekday_teetime:
            generate('weekday')
            curr_week.weekday_teetimes = True
            db.session.commit()

        if not curr_week.weekend_teetimes and curr_week.weekend_request and  calendar.day_name[now.weekday()] == weekend_teetime:
            generate('weekend')
            curr_week.weekend_teetimes = True
            curr_week.closed = True
            db.session.commit()

        sleep_until_midnight()

def sleep_until_midnight():

    next_cycle = dt.now() + timedelta(days=1)
    next_cycle.replace(hour=0,minute=1,second=0)
    sleep_time = (next_cycle-dt.now()).total_seconds()
    time.sleep(sleep_time)

if __name__ == '__main__':
    loft_process()
