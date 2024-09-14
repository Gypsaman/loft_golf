from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import login_required
from webproject.modules.table_creator import Field, TableCreator, timestamp_to_date, true_false, time_to_day_time
from webproject.models import Weeks
from webproject.modules.extensions import db
from datetime import datetime as dt


weeks = Blueprint('weeks', __name__)
@weeks.route('/weeks')
@login_required
def weeks_table():
    fields = {
        'id': Field(None,None),
        'start_date': Field(timestamp_to_date,'Start Date'),
        'end_date': Field(timestamp_to_date,'End Date'),
        'weekday_request': Field(true_false,'Weekday Request'),
        'weekend_request': Field(true_false,'Weekend Request'),
        'weekday_teetimes': Field(true_false,'Weekday Tee Times'),
        'weekend_teetimes': Field(true_false,'Weekend Tee Times'),
        'closed': Field(true_false,'Closed')
    }
    table_creator = TableCreator('Weeks', fields,actions=['Edit', 'Delete'])
    table_creator.set_items_per_page(15)
    table_creator.create_view(order='start_date')
    table = table_creator.create(1)

    return render_template("weeks/weeks.html", table=table)

@weeks.route('/weeks/update/<int:id>', methods=['GET'])
@login_required
def update_week(id):
    week = Weeks.query.filter_by(id=id).first()
    tee_times = teetimes_table(week.id)
    return render_template("weeks/update_week.html",week=week,tee_times=tee_times)

@weeks.route('/weeks/update/<int:id>', methods=['POST'])
@login_required
def update_week_post(id):
    week = Weeks.query.filter_by(id=id).first()
    week.start_date = dt.strptime(request.form.get('start_date'),"%Y-%m-%d")
    week.end_date = dt.strptime(request.form.get('end_date'),"%Y-%m-%d")
    week.closed = True if request.form.get('closed')  else False
    db.session.commit()
    return redirect(url_for('weeks.weeks_table'))

@weeks.route('/weeks/add')
@login_required
def add_week():
    return render_template("weeks/add_week.html")

@weeks.route('/weeks/add', methods=['POST'])
@login_required
def add_week_post():
    week = Weeks(start_date=dt.strptime(request.form.get('start_date'),"%Y-%m-%d"), 
                 end_date=dt.strptime(request.form.get('end_date'), "%Y-%m-%d"),
                closed=True if request.form.get('closed') else False)
    db.session.add(week)
    db.session.commit()
    return redirect(url_for('weeks.weeks_table'))

@weeks.route('/weeks/delete/<int:id>')
@login_required
def delete_week(id):
    week = Weeks.query.filter_by(id=id).first()
    db.session.delete(week)
    db.session.commit()
    return redirect(url_for('weeks.weeks_table'))

# Tee Times Section
#
#

def teetimes_table(week_id):
    fields = {
        'teetimes.id': Field(None,None),
        'time': Field(time_to_day_time,'Time'),
        'holiday': Field(true_false,'Holiday'),
        'teetimes.closed': Field(true_false,'Closed')
    }
    table_creator = TableCreator('TeeTimes', condition=f'week_id={week_id}',fields=fields,actions=['Edit', 'Delete'])
    table_creator.join("Weeks", "teetimes.week_id = weeks.id")
    table_creator.set_items_per_page(15)
    table_creator.create_view(order='time')
    table = table_creator.create(1)

    return table