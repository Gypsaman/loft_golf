from webproject.modules.loftemail import Email
from webproject.modules.utils import get_curr_week, day_order
from webproject.models import Players, TeeTimes
from datetime import timedelta
from datetime import datetime as dt
from webproject.modules.extensions import db
from sqlalchemy import text


def announcements(msg,weekday,weekend):
    sql = 'select players.first_name,players.email from Players '
    sql += "Where Players.weekday = 1 or Players.weekend = 1 " if weekday and weekend else ""
    sql += 'Where weekday  = 1' if weekday and not weekend else ""
    sql += 'Where weekend = 1' if weekend and not weekday else ""

    players = list(db.session.execute(text(sql)))
    email = Email()
    for player in players:
        email_body = f'Dear {player.first_name},\n\n'
        email_body += msg
        email.send_email(player.email,"Announcement",email_body)

 
def submission_received(submission):

    curr_week = submission.week
    player = Players.query.filter_by(id=submission.player_id).first()
    email = Email()
    body = f"Dear {player.first_name},\n\n"
    body += "Your tee time request has been received. You requested the following days "
    body += f"for the week of {curr_week.start_date.strftime('%B %d')} through {curr_week.end_date.strftime('%B %d')}:\n\n"
    for idx,day in enumerate(day_order):
        if getattr(submission,day):
            body += f"{day}, {(curr_week.start_date + timedelta(days=idx)).strftime('%B %d')}"
            if getattr(submission,day+'_guest'):
                body += " with a guest"
            body += "\n"
    body += "\n\nYou will receive an email when your tee times are assigned.\n\n"
    email.send_email(player.email,'Tee Time Request Received',body)

def tee_time_assigned(curr_week,category):
    start = 0 if category == 'weekday' else 4
    end = 3 if category == 'weekday' else 6
    start_date = curr_week.start_date  + timedelta(days=start)
    end_date = curr_week.start_date + timedelta(days=end)


    sql = "Select players.first_name, players.last_name, players.email, teetimes.time from teetimeplayers"
    sql += " join players on teetimeplayers.player_id = players.id "
    sql += " join teetimes on teetimeplayers.tee_time_id = teetimes.id "
    sql += f" where teetimes.time >= '{start_date}' and teetimes.time < '{end_date}'"
    sql += " order by teetimes.time"

    teetimes = list(db.session.execute(text(sql)))
    teetable =  tee_time_table(teetimes)

    body = f"Here are the tee times you requested, along with the other pairings "
    body += f"for {start_date.strftime('%b-%d')} to {(end_date - timedelta(days=1)).strftime('%b-%d')}:\n\n"


    email = Email()
    player_sent = []
    for teetime in teetimes:
        if teetime.email in player_sent:
            continue
        player_sent.append(teetime.email)
        email_body = f'<p>{teetime.first_name},\n\n</p>'
        email_body +=f'<p>{body}</p>'
        email_body += teetable
        email.send_multipart_email(teetime.email,'Tee Time Assignment',email_body,carboncopy='gypsaman@gmail.com')


def tee_time_added(tee_time,is_old,is_dup,requester):
    email = Email()
    body = f"A new tee time has been added for {tee_time.time.strftime('%A %b-%d %H:%M')}.\n"
    if is_old:
        body += "\nThis is for an older week than the current one. Please check the system."
    elif is_dup:
        body = f"A request to add {tee_time.time.strftime('%A %b-%d %H:%M')} has been received.\n\n This is a duplicate entry, No action taken."
    email.send_email(requester,'Tee Time Added',body)


def tee_time_table(teetimes):

    html = '<table>'+'\n'
    html += '<tbody>'+'\n'
    html += '<tr style="height:.25in">'+'\n'
    html += '<td style="width:1in;background-color:#4472c4;; color:yellow;text-align: center;">Date</td>'+'\n'
    html += '<td style="width:3in;background-color:#4472c4;; color:yellow;text-align: center;">Golfer</td>'+'\n'
    html += '<td style="width:1in;background-color:#4472c4;; color:yellow;text-align: center;">Tee Time</td>'+'\n'
    html += '</tr>'+'\n'
    
    curr_tee = None
    row = 0
    for teetime in teetimes:
        html += '<tr>'+'\n'
        if curr_tee is None or curr_tee != teetime.time:
           row = 5 if not curr_tee else row+1
           for i in range(row,5):
               html += '<tr><td></td><td></td></tr>'+'\n'
           row = 0
           
           if curr_tee:
                html += '<tr><td style="background-color:blue"></td><td style="background-color:blue"></td><td style="background-color:blue"></td></tr>'+'\n'

           html += '<td rowspan="4">'+ dt.strptime(teetime.time[:-7],"%Y-%m-%d %H:%M:%S").strftime('%A %B %d') + '</td>'+'\n'
           curr_tee = teetime.time
           
        
        html += f'<td style="width:3in">{teetime.first_name} {teetime.last_name}</td> \n'
        html += f'<td style="width:1in">{dt.strptime(teetime.time[:-7],"%Y-%m-%d %H:%M:%S").strftime("%H:%M")}</td> \n'
        html += '</tr>'+'\n'
        row = row + 1
               
    for i in range(row,5):
        html += '<tr><td></td><td></td></tr>'+'\n'
        

    html += '<tr><td style="background-color:blue"></td><td style="background-color:blue"></td><td style="background-color:blue"></td></tr>'+'\n'
    html += '</tbody>'+'\n'

    html += '</table>'+'\n'

    return html

def tee_times_available(curr_week,category):
    start = 0 if category == 'weekday' else 4
    end = 3 if category == 'weekday' else 6
    start_date = curr_week.start_date  + timedelta(days=start)
    end_date = curr_week.start_date + timedelta(days=end)

    teetimes = TeeTimes.query.filter(TeeTimes.time>=start_date,TeeTimes.time <= end_date).order_by(TeeTimes.time).all()

    # sql = "Select teetimes.time from teetimes"
    # sql += f" where teetimes.time >= '{start_date}' and teetimes.time < '{end_date}'"
    # sql += " order by teetimes.time"
    # teetimes = list(db.session.execute(text(sql)))


    body = f"Here are the tee times availables "
    body += f"for {start_date.strftime('%b-%d')} to {(end_date - timedelta(days=1)).strftime('%b-%d')}:\n\n"


    email = Email()
    sql = "Select players.first_name, players.last_name, players.email, players.access_code from Players"
    sql += f" where {category} "
    players = list(db.session.execute(text(sql)))
    for player in players:
        email_body = f'<p>{player.first_name},\n\n</p>'
        email_body += f'<p>{body}</p>'
        email_body += '<p>\nPlease follow the link below to request your tee times\n\n</p>'
        email_body += f'<a href="loft.neurodna.xyz/requests/{category}/{player.access_code} " >loft.neurodna.xyz/requests/{category}/{player.access_code}</a>'
        email_body += '<p>\n\n</p>'
        email_body +=  tee_avail_table(teetimes,email_body)
        email.send_multipart_email(player.email,'Tee Times Available',email_body,carboncopy='gypsaman@gmail.com')


def tee_avail_table(teetimes,email_body):
    dates_avail = {}
    for teetime in teetimes:
        day =  teetime.time.strftime('%A %b %d') 
        if day not in dates_avail:
            dates_avail[day]  = []
        dates_avail[day].append(teetime.time.strftime('%H:%M'))

    html = '<table>'+'\n'
    html += '<tbody>'+'\n'
    html += '<tr style="height:.25in">'+'\n'
    html += '<td style="width:2in;background-color:#4472c4;; color:yellow;text-align: center;">Date</td>'+'\n'
    html += '<td style="width:1in;background-color:#4472c4;; color:yellow;text-align: center;">Tee Time</td>'+'\n'
    html += '</tr>'+'\n'
    
    curr_tee = None
    for teedate,times in dates_avail.items():
        html += '<tr>'+'\n'

        html += f'<td rowspan={len(times)}>'+ teedate + '</td>'+'\n'
        for time in times:
            html += f'<td style="width:1in">{time}</td>\n'
            html += '</tr>'+'\n'
            html += '<tr>\n'
        html += '</tr>'
        html += '<tr><td style="background-color:blue"></td><td style="background-color:blue"></td></tr>'+'\n'

               
    

    html += '<tr><td style="background-color:blue"></td><td style="background-color:blue"></td></tr>'+'\n'
    html += '</tbody>'+'\n'

    html += '</table>'+'\n'

    return html

def tee_table(teetimes,golfer=True):
    dates_avail = {}
    for teetime in teetimes:
        teedate = dt.strptime(teetime.time[:-10],"%Y-%m-%d %H:%M")
        day =  teedate.strftime('%A %b %d') 
        if day not in dates_avail:
            dates_avail[day]  = []
        golfer_name = teetime.first_name + ' ' + teetime.last_name if golfer else ''
            
        dates_avail[day].append({"teetime":teedate.strftime('%H:%M'),"golfer":golfer_name})

    html = '<table>'+'\n'
    html += '<tbody>'+'\n'
    html += '<tr style="height:.25in">'+'\n'
    html += '<td style="width:2in;background-color:#4472c4;; color:yellow;text-align: center;">Date</td>'+'\n'
    if golfer:
            html += '<td style="width:3in;background-color:#4472c4;; color:yellow;text-align: center;">Golfer</td>'+'\n'
    html += '<td style="width:1in;background-color:#4472c4;; color:yellow;text-align: center;">Tee Time</td>'+'\n'
    html += '</tr>'+'\n'
    
    curr_tee = None
    for teedate,times in dates_avail.items():
        html += '<tr>'+'\n'

        html += f'<td rowspan={len(times)}>'+ teedate + '</td>'+'\n'
        for time in times:
            if golfer:
                html += f'<td style="width:1in">{time['golfer']}</td>\n'
            html += f'<td style="width:1in">{time['teetime']}</td>\n'
            html += '</tr>'+'\n'
            html += '<tr>\n'
        html += '</tr>'
        html += f'<tr>'
        if golfer:
            html += '<td style="background-color:blue"></td>'
        html += '<td style="background-color:blue"></td><td style="background-color:blue"></td></tr>'+'\n'

               
    html += f'<tr>'
    if golfer:
        html += '<td style="background-color:blue"></td>'
    html += '<td style="background-color:blue"></td><td style="background-color:blue"></td></tr>'+'\n'

    html += '</tbody>'+'\n'

    html += '</table>'+'\n'

    return html
