from park import db

class ParkData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(80), nullable=False)
    event = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(80), nullable=False)