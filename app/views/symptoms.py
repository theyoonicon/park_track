from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from flask_jwt_extended import jwt_required
from ..models import Symptom, User
from ..data_processiong import create_interactive_graph, query_to_dataframe, create_graph
from .. import db, ma
from .auth import get_jwt_identity_from_request

symptoms_bp = Blueprint('symptoms', __name__)

class SymptomSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'time', 'event', 'type')

symptom_schema = SymptomSchema()
symptoms_schema = SymptomSchema(many=True)

@symptoms_bp.route('/symptoms', methods=['GET', 'POST'])
@jwt_required(optional=True)
def get_or_add_symptoms():
    try:
        if request.headers.get('Accept') == 'application/json':
            user_id=get_jwt_identity_from_request()
        else:
            user_id = session.get('user_id')
        if not user_id:
            return jsonify({"message": "Unauthorized access"}), 401
        user = User.query.get(user_id)
        if user:
            print(user)
            print(request.method)
            if request.method == 'POST':
                data = request.get_json(force=True)
                time = data.get('time')
                event = data.get('event')
                type = data.get('type')
                new_symptom = Symptom(username=user.username, time=time, event=event, type=type)
                db.session.add(new_symptom)
                db.session.commit()
                return symptom_schema.jsonify(new_symptom), 201
            else:
                symptoms = Symptom.query.filter_by(username=user.username)
                date_filter = request.args.get('date_filter')
                if date_filter:
                    symptoms = symptoms.filter(Symptom.time.like(f'%{date_filter}%'))
                symptoms = symptoms.all()
                df = query_to_dataframe(symptoms)
                graph_html = create_interactive_graph(df)
                if request.headers.get('Accept') == 'application/json':
                    return symptoms_schema.jsonify(symptoms), 200
                return render_template('symptoms.html', graph_html=graph_html, symptoms=symptoms, tables=[df.to_html(classes='data table table-bordered')], titles=df.columns.values)
        return jsonify({"message": "Unauthorized access"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@symptoms_bp.route('/symptoms/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_symptom(id):
    try:
        if request.headers.get('Accept') == 'application/json':
            user_id=get_jwt_identity_from_request()
        else:
            user_id = session.get('user_id')
        if not user_id:
            return jsonify({"message": "Unauthorized access"}), 401
        user = User.query.get(user_id)
        if user:
            symptom = Symptom.query.get(id)
            if symptom and symptom.username == user.username:
                data = request.get_json(force=True)
                symptom.event = data.get('event', symptom.event)
                symptom.type = data.get('type', symptom.type)
                db.session.commit()
                return symptom_schema.jsonify(symptom), 200
        return jsonify({"message": "Unauthorized access"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@symptoms_bp.route('/symptoms/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_symptom(id):
    try:
        if request.headers.get('Accept') == 'application/json':
            user_id=get_jwt_identity_from_request()
        else:
            user_id = session.get('user_id')
        if not user_id:
            return jsonify({"message": "Unauthorized access"}), 401
        user = User.query.get(user_id)
        if user:
            symptom = Symptom.query.get(id)
            if symptom and symptom.username == user.username:
                db.session.delete(symptom)
                db.session.commit()
                return symptom_schema.jsonify(symptom), 200
        return jsonify({"message": "Unauthorized access"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@symptoms_bp.route('/symptom_check', methods=['GET', 'POST'])
@jwt_required(optional=True)
def symptom_check():
    if request.headers.get('Accept') == 'application/json':
        user_id=get_jwt_identity_from_request()
    else:
        user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized access"}), 401
    user = User.query.get(user_id)
    if user:
        if request.method == 'POST':
            event = request.form.get('event')
            type = request.form.get('type')
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_symptom = Symptom(username=user.username, time=time, event=event, type=type)
            db.session.add(new_symptom)
            db.session.commit()
            return redirect(url_for('symptoms.get_or_add_symptoms'))
        return render_template('symptom_check.html')
    return jsonify({"message": "Unauthorized access"}), 401
