from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import current_user, login_required
from webproject.modules.table_creator import Field, TableCreator, timestamp_to_date, true_false


main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template("main/index.html")

@main.route('/weather')
@login_required
def weather():
    return render_template("main/weather.html")

