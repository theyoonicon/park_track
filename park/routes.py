from flask import Blueprint, jsonify, request
from .models import ParkData
from . import db

park_bp = Blueprint('park', __name__)

@park_bp.route('/', methods=['GET'])
def get_park_data():
    park_data = ParkData.query.all()
    result = [
        {
            "id": data.id,
            "time": data.time,
            "event": data.event,
            "type": data.type
        } for data in park_data
    ]
    return jsonify(result)

@park_bp.route('/', methods=['POST'])
def add_park_data():
    new_data = request.get_json()
    park_data = ParkData(
        time=new_data['time'],
        event=new_data['event'],
        type=new_data['type']
    )
    db.session.add(park_data)
    db.session.commit()
    return jsonify({"message": "Park data added successfully!"}), 201
