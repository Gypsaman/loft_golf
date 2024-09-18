from webproject.loft_app import app, db
from sqlalchemy import text
# from webproject.models import Players, User, Weeks, TeeTimes, TeeRequests
# from webproject.modules.utils import get_curr_week
# import hashlib
# from werkzeug.security import generate_password_hash
# from datetime import datetime as dt


with app.app_context():
    weekday = False
    weekend = False
    sql = 'select players.first_name,players.email from Players '
    sql += "Where Players.weekday = 1 or Players.weekend = 1 " if weekday and weekend else ""
    sql += 'Where weekday  = 1' if weekday and not weekend else ""
    sql += 'Where weekend = 1' if weekend and not weekday else ""

    players = list(db.session.execute(text(sql)))
    for player in players:
        print(player)
    

