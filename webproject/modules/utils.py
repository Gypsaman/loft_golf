from webproject.models import Weeks




day_order = ['Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','Monday']
def get_curr_week():
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    if curr_week:
        return curr_week
    curr_week = Weeks.query.filter(Weeks.closed==True).order_by(Weeks.start_date.desc()).first()
    return curr_week
