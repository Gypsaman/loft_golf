# from webproject.modules.process_emails import process_emails
# from webproject.loft_app import app, db
# from webproject.models import Players, User, Weeks, TeeTimes, TeeRequests, TeeTimePlayers
# from collections import Counter
# from webproject.routes.requests import get_committed_requests, day_order, group_requests,is_player_booked
# from datetime import datetime as dt
# from datetime import timedelta
# from sqlalchemy import text
# from webproject.modules  import messaging 
# from webproject.modules.loftemail import Email
# from webproject.modules.process_emails import process_emails


# with app.app_context():
#     process_emails()


from webproject.routes.requests import group_requests,check_guests

def test_check_guests():
    for _ in range(100):
        players = [2,4,1,6,7,8]
        guests = [7,2,4]
        groups = group_requests(players,guests)
        if len([group for group in groups if len(group) > 4]) == 0:
            continue
        else:
            print(groups)
    # assert groups[1] == [7,7]

test_check_guests()
