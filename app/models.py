from . import db, ma

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password

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
