from . import db, ma
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=True)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    @property
    def is_active(self):
        # Here you can add conditions for inactive users if needed
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('user.username'))
    time = db.Column(db.String(100))
    event = db.Column(db.String(100))
    type = db.Column(db.String(100))

    def __init__(self, username, time, event, type):
        self.username = username
        self.time = time
        self.event = event
        self.type = type
