from flask_login import UserMixin
from .modules.extensions import db
from datetime import datetime



class Players(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    weekday = db.Column(db.Boolean, nullable=False)
    weekend = db.Column(db.Boolean, nullable=False)
    ghin = db.Column(db.String(10), nullable=True)
    handicap = db.Column(db.Float, nullable=False)
    access_code = db.Column(db.String(4), nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'{self.first_name} {self.last_name}, {self.email}, {self.phone}, {self.weekday}, {self.weekend}, {self.ghin}, {self.handicap}, {self.access_code}, {self.active}'
    


class TeeTimes(db.Model):
    __tablename__ = 'teetimes'
    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'))
    time = db.Column(db.DateTime, nullable=False)
    holiday = db.Column(db.Boolean, nullable=False, default=False)
    closed = db.Column(db.Boolean, nullable=False)

class TeeTimePlayers(db.Model):
    __tablename__ = 'teetimeplayers'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    tee_time_id = db.Column(db.Integer, db.ForeignKey('teetimes.id'))
    player = db.relationship('Players', backref='teetimeplayers')
    tee_time = db.relationship('TeeTimes', backref='teetimeplayers')

    def __repr__(self):
        return f'Player: {self.player.first_name} {self.player.last_name} Tee Time: {self.tee_time.time}'

# class TeeRequests(db.Model):
#     __tablename__ = 'teerequests'
#     id = db.Column(db.Integer, primary_key=True)
#     player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
#     week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'))
#     Monday = db.Column(db.Boolean, nullable=False)
#     Tuesday = db.Column(db.Boolean, nullable=False)
#     Wednesday = db.Column(db.Boolean, nullable=False)
#     Thursday = db.Column(db.Boolean, nullable=False)
#     Friday = db.Column(db.Boolean, nullable=False)
#     Saturday = db.Column(db.Boolean, nullable=False)
#     Sunday = db.Column(db.Boolean, nullable=False)
#     player = db.relationship('Players', backref='teerequests')
#     week = db.relationship('Weeks', backref='teerequests')

#     def __repr__(self):
#         return f'Player: {self.player.first_name} Week: {self.week.start_date.strftime("%b-%d")} Monday: {self.Monday}, Tuesday: {self.Tuesday}, Wednesday: {self.Wednesday}, Thursday: {self.Thursday}, Friday: {self.Friday}, Saturday: {self.Saturday}, Sunday: {self.Sunday}'

class TeeRequests(db.Model):
    __tablename__ = 'teerequests'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'))
    date_requested = db.Column(db.DateTime, nullable=False)
    processed = db.Column(db.Boolean, nullable=False)
    player = db.relationship('Players', backref='teerequests')
    week = db.relationship('Weeks', backref='teerequests')
    

class Weeks(db.Model):
    __tablename__ = 'weeks'
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    closed = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f'start_date: {self.start_date}, end_date: {self.end_date}, closed: {self.closed}'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def get_urole(self):
        return self.role

    def __repr__(self):
        return f'<User {self.username}>'
    
class PasswordReset(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    password_phrase = db.Column(db.Integer)
    phrase_expires = db.Column(db.DateTime)
    
    def get_password_phrase(self):
        return self.password_phrase
    
    def get_password_phrase_expiry(self) -> datetime:
        return self.phrase_expires
    
    def __repr__(self):
        return f'password_phrase: {self.password_phrase}, phrase_expires: {self.phrase_expires}'
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "password_phrase": self.password_phrase,
            "phrase_expires": self.phrase_expires
        }