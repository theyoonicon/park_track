from . import db, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

class ParkData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.String(80), nullable=False)
    event = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(80), nullable=False)

    def __init__(self, user_id, time, event, type):
        self.user_id = user_id
        self.time = time
        self.event = event
        self.type = type
