from datetime import datetime
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required
from ..models import Symptom, User
from .. import db, ma
from .auth import get_jwt_identity_from_request

symptoms_bp = Blueprint('symptoms', __name__)

class SymptomSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'time', 'event', 'type')

symptom_schema = SymptomSchema()
symptoms_schema = SymptomSchema(many=True)

@symptoms_bp.route('/<username>/symptoms', methods=['GET', 'POST'])
@jwt_required(optional=True)
def get_or_add_symptoms(username):
    try:
        user_id = get_jwt_identity_from_request()
        if not user_id:
            return jsonify({"message": "Unauthorized access"}), 401
        user = User.query.get(user_id)
        if user and user.username == username:
            if request.method == 'POST':
                data = request.get_json(force=True)
                time = data.get('time')
                event = data.get('event')
                type = data.get('type')
                new_symptom = Symptom(username=username, time=time, event=event, type=type)
                db.session.add(new_symptom)
                db.session.commit()
                return symptom_schema.jsonify(new_symptom), 201
            else:
                symptoms = Symptom.query.filter_by(username=username).all()
                date_filter = request.args.get('date_filter')
                if date_filter:
                    symptoms = symptoms.filter(Symptom.time.like(f'%{date_filter}%'))
                symptoms = symptoms.all()
                if request.headers.get('Accept') == 'application/json':
                    return symptoms_schema.jsonify(symptoms), 200
                return render_template('symptoms.html', symptoms=symptoms)
        return jsonify({"message": "Unauthorized access"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@symptoms_bp.route('/<username>/symptoms/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_symptom(username, id):
    try:
        user_id = get_jwt_identity_from_request()
        if not user_id:
            return jsonify({"message": "Unauthorized access"}), 401
        user = User.query.get(user_id)
        if user and user.username == username:
            symptom = Symptom.query.get(id)
            if symptom and symptom.username == username:
                data = request.get_json(force=True)
                symptom.event = data.get('event', symptom.event)
                symptom.type = data.get('type', symptom.type)
                db.session.commit()
                return symptom_schema.jsonify(symptom), 200
        return jsonify({"message": "Unauthorized access"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@symptoms_bp.route('/<username>/symptoms/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_symptom(username, id):
    try:
        user_id = get_jwt_identity_from_request()
        if not user_id:
            return jsonify({"message": "Unauthorized access"}), 401
        user = User.query.get(user_id)
        if user and user.username == username:
            symptom = Symptom.query.get(id)
            if symptom and symptom.username == username:
                db.session.delete(symptom)
                db.session.commit()
                return symptom_schema.jsonify(symptom), 200
        return jsonify({"message": "Unauthorized access"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
