from flask import Blueprint, request, jsonify, render_template
from ..models import User, ParkData
from .. import db, ma
from .auth import get_jwt_identity_from_request

symptoms_bp = Blueprint('symptoms', __name__)

class ParkDataSchema(ma.Schema):
    class Meta:
        fields = ('id', 'time', 'event', 'type')

park_data_schema = ParkDataSchema()
park_datas_schema = ParkDataSchema(many=True)

@symptoms_bp.route('/<username>/symptoms', methods=['GET'])
def get_symptoms(username):
    try:
        user_id = get_jwt_identity_from_request()
        if not user_id:
            return jsonify({"message": "Unauthorized access"}), 401
        user = User.query.filter_by(id=user_id).first()
        if user and user.username == username:
            all_symptoms = ParkData.query.filter_by(user_id=user.id).all()
            result = park_datas_schema.dump(all_symptoms)
            if request.headers.get('Accept') == 'application/json':
                return jsonify(result)
            return render_template('symptoms.html', symptoms=result)
        return jsonify({"message": "Unauthorized access"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@symptoms_bp.route('/<username>/symptoms', methods=['POST'])
def add_symptom(username):
    try:
        user_id = get_jwt_identity_from_request()
        if not user_id:
            return jsonify({"message": "Unauthorized access"}), 401
        user = User.query.filter_by(id=user_id).first()
        if user and user.username == username:
            data = request.get_json(force=True, silent=True)
            if data is None:
                return jsonify({"message": "Invalid JSON data"}), 400
            time = data.get('time')
            event = data.get('event')
            type = data.get('type')
            new_symptom = ParkData(user_id=user.id, time=time, event=event, type=type)
            db.session.add(new_symptom)
            db.session.commit()
            return park_data_schema.jsonify(new_symptom), 201
        return jsonify({"message": "Unauthorized access"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
