from flask import Blueprint, jsonify, request
# from .models import ParkData
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

@park_bp.route('/<int:id>', methods=['PUT'])
def update_park_data(id):
    update_data = request.get_json()
    park_data = ParkData.query.get_or_404(id)
    park_data.time = update_data['time']
    park_data.event = update_data['event']
    park_data.type = update_data['type']
    db.session.commit()
    return jsonify(update_data), 200

@park_bp.route('/<int:id>', methods=['DELETE'])
def delete_park_data(id):
    park_data = ParkData.query.get_or_404(id)
    db.session.delete(park_data)
    db.session.commit()
    return '', 204
