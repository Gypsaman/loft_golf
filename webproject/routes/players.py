from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import current_user, login_required
from webproject.modules.extensions import db
from webproject.modules.table_creator import Field, TableCreator, timestamp_to_date, true_false,round_to_2_decimals
# from datetime import datetime as dt
from webproject.models import Players
import hashlib

players = Blueprint('players', __name__)



@players.route('/players/<int:page_num>')
@login_required
def players_table(page_num):
    fields = {
        'id': Field(None,None),
        'first_name': Field(None,'Name'),
        'last_name': Field(None,'Last Name'),
        'email': Field(None,'Email'),
        'phone': Field(None,'Phone'),
        'weekday': Field(true_false,'Weekday'),
        'weekend': Field(true_false,'Weekend'),
        'ghin': Field(None,'GHIN'),
        'handicap': Field(round_to_2_decimals,'Handicap'),
        'active': Field(true_false,'Active')
    }
    table_creator = TableCreator('Players', fields,actions=['Edit', 'Delete'])
    table_creator.set_items_per_page(15)
    table_creator.create_view(order='last_name')
    table = table_creator.create(page_num)

    return render_template("players/players.html", table=table)


@players.route('/players/update/<int:id>', methods=['GET'])
@login_required
def update_player(id):
    player = Players.query.filter_by(id=id).first()
    return render_template("players/update_player.html",player=player)

@players.route('/players/update/<int:id>', methods=['POST'])
@login_required
def update_player_post(id):
    player = Players.query.filter_by(id=id).first()
    player.first_name = request.form.get('first_name')
    player.last_name = request.form.get('last_name')
    player.email = request.form.get('email')
    player.phone = request.form.get('phone')
    player.weekday = True if request.form.get('weekday')  else False
    player.weekend = True if request.form.get('weekend') else False
    player.ghin = request.form.get('ghin')
    player.handicap = request.form.get('handicap')
    player.active = True if request.form.get('active') else False
    db.session.commit()
    return redirect(url_for('players.players_table', page_num=1))


@players.route('/players/add')
@login_required
def add_player():
    return render_template("players/add_player.html")

@players.route('/players/add', methods=['POST'])
@login_required
def add_player_post():
    email = request.form.get('email')
    player = Players(
    first_name = request.form.get('first_name'),
    last_name = request.form.get('last_name'),
    email = email,
    phone = request.form.get('phone'),
    weekday = True if request.form.get('weekday')  else False,
    weekend = True if request.form.get('weekend') else False,
    ghin = request.form.get('ghin'),
    handicap = request.form.get('handicap'),
    active = True if request.form.get('active') else False,
    access_code= hashlib.sha256(email.encode()).hexdigest()[:4],
    )
    db.session.add(player)
    db.session.commit()
    
    return redirect(url_for('players.players_table', page_num=1))

@players.route('/players/delete/<int:id>')
@login_required
def delete_player(id):
    player = Players.query.filter_by(id=id).first()
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('players.players_table', page_num=1))