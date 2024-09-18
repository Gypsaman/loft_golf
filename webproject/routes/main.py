from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import login_required
from webproject.modules import messaging



main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template("main/index.html")

@main.route('/weather')
@login_required
def weather():
    return render_template("main/weather.html")

@main.route('/announcements')
@login_required
def announcements():
    return render_template("main/announcements.html")

@main.route('/announcements', methods=['POST'])
@login_required
def announcements_post():
    msg = request.form.get('message')
    weekday = request.form.get('weekday')
    weekend = request.form.get('weekend')
    messaging.announcements(msg,weekday,weekend)

    return redirect(url_for('main.weather'))