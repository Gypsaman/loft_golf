from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import login_required



main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template("main/index.html")

@main.route('/weather')
@login_required
def weather():
    return render_template("main/weather.html")

