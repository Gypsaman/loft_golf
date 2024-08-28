from flask import Blueprint, redirect, render_template,  request, url_for, flash
from flask_login import login_required
from webproject.modules.extensions import db
from webproject.models import TeeTimes, Weeks, TeeTimePlayers
from webproject.modules.table_creator import TableCreator, Field, time_to_day_time
from datetime import datetime as dt


teetimes = Blueprint('teetimes', __name__)

@teetimes.route('/teetimes/update/<int:id>', methods=['GET'])
@login_required
def update_teetime(id):
    teetime = TeeTimes.query.filter_by(id=id).first()
    week = Weeks.query.filter_by(id=teetime.week_id).first()
    return render_template("teetimes/update_teetime.html",teetime=teetime,week=week)

@teetimes.route('/teetimes/update/<int:id>', methods=['POST'])
@login_required
def update_teetime_post(id):
    teetime = TeeTimes.query.filter_by(id=id).first()
    teetime.time = dt.strptime(request.form.get('teetime'),"%Y-%m-%dT%I:%M")
    teetime.holiday = True if request.form.get('holiday') else False
    teetime.closed = True if request.form.get('closed') else False
    db.session.commit()
    return redirect(url_for('weeks.update_week',id=teetime.week_id))

@teetimes.route('/teetimes/add/<int:week_id>')
@login_required
def add_teetime(week_id):
    week = Weeks.query.filter_by(id=week_id).first()
    return render_template("teetimes/add_teetime.html",week=week)

@teetimes.route('/teetimes/add', methods=['POST'])
@login_required
def add_teetime_post():
    week_id = request.form.get('week_id')
    time = dt.strptime(request.form.get('teetime'),"%Y-%m-%dT%I:%M")
    week = Weeks.query.filter_by(id=week_id).first()
    if time < week.start_date or time > week.end_date:
        flash('Tee time must be within the week.')
        return redirect(url_for('weeks.update_week',id=week_id))
    teetime = TeeTimes(
        week_id=week_id,
        time=time, 
        holiday = True if request.form.get('holiday') else False,
        closed=True if request.form.get('closed') else False
    )
    db.session.add(teetime)
    db.session.commit()
    return redirect(url_for('weeks.update_week',id=teetime.week_id)) 

@teetimes.route('/teetimes/delete/<int:id>')
@login_required
def delete_teetime(id):
    teetime = TeeTimes.query.filter_by(id=id).first()
    week_id = teetime.week_id
    db.session.delete(teetime)
    db.session.commit()
    return redirect(url_for('weeks.update_week',id=week_id))


@teetimes.route('/pairings')
@login_required
def pairings():
    curr_week = Weeks.query.filter(Weeks.closed==False).order_by(Weeks.start_date).first()
    teetimes = [tee.id for tee in TeeTimes.query.filter_by(week_id=curr_week.id).all()]
    groupings = TeeTimePlayers.query.filter(TeeTimePlayers.tee_time_id.in_(teetimes)).all()
    fields = {
        'player_id': Field(None,None),
        'tee_time.time': Field(time_to_day_time,'Time')
    }
    table_creator = TableCreator('TeeTimePlayers', fields)
    table_creator.set_items_per_page(15)
    table_creator.create_view()
    table = table_creator.create(1)
    return render_template("teetimes/pairings.html",table=table)