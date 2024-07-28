from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import jwt_required
from ..models import Symptom, User
from .. import db, ma
from .auth import get_jwt_identity_from_request

import matplotlib.pyplot as plt
import matplotlib
plt.rc('font', family='Malgun Gothic')
matplotlib.use('Agg')
import matplotlib.dates as mdates

import io
import base64

import pandas as pd

import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio

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
                symptoms = Symptom.query.filter_by(username=username)
                date_filter = request.args.get('date_filter')
                if date_filter:
                    symptoms = symptoms.filter(Symptom.time.like(f'%{date_filter}%'))
                symptoms = symptoms.all()
                df = query_to_dataframe(symptoms)
                # graph_url = create_graph(df)
                graph_html = create_interactive_graph(df)
                if request.headers.get('Accept') == 'application/json':
                    return symptoms_schema.jsonify(symptoms), 200
                return render_template('symptoms.html', graph_html=graph_html, symptoms=symptoms, tables=[df.to_html(classes='data table table-bordered')], titles=df.columns.values)
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


# 새로운 엔드포인트 추가
@symptoms_bp.route('/<username>/symptom_check', methods=['GET', 'POST'])
@jwt_required(optional=True)
def symptom_check(username):
    user_id = get_jwt_identity_from_request()
    if not user_id:
        return jsonify({"message": "Unauthorized access"}), 401
    user = User.query.get(user_id)
    if user and user.username == username:
        if request.method == 'POST':
            event = request.form.get('event')
            type = request.form.get('type')
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_symptom = Symptom(username=username, time=time, event=event, type=type)
            db.session.add(new_symptom)
            db.session.commit()
            return redirect(url_for('symptoms.get_or_add_symptoms', username=username))
        return render_template('symptom_check.html', username=username)
    return jsonify({"message": "Unauthorized access"}), 401

# 새로운 선택 화면 엔드포인트 추가
@symptoms_bp.route('/<username>/choose_action', methods=['GET'])
@jwt_required(optional=True)
def choose_action(username):
    user_id = get_jwt_identity_from_request()
    if not user_id:
        return jsonify({"message": "Unauthorized access"}), 401
    user = User.query.get(user_id)
    if user and user.username == username:
        return render_template('home.html', username=username)
    return jsonify({"message": "Unauthorized access"}), 401

# pandas
def query_to_dataframe(query):
    """ Convert query result to Pandas DataFrame """
    data = []
    for symptom in query:
        data.append({
            'id': symptom.id,
            'username': symptom.username,
            'time': symptom.time,
            'event': symptom.event,
            'type': symptom.type
        })
    return pd.DataFrame(data)

def create_graph(df):
    """ Create a graph from the DataFrame and return as base64 string """
    plt.figure(figsize=(10, 5))
    
    if df.empty:
        plt.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', fontsize=12)
        plt.axis('off')
    else:
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        events = {"좋아요": 1, "보통이에요": 2, "나빠요": 3}
        df['event_num'] = df['event'].map(events)

        plt.plot(df['time'], df['event_num'], marker='o', linestyle='-', color='b', label='Event')
        
        for i, row in df.iterrows():
            if row['event'] == '약 섭취':
                plt.annotate('약 섭취', xy=(row['time'], row['event_num']),
                             xytext=(row['time'], row['event_num'] + 0.3),
                             arrowprops=dict(facecolor='red', shrink=0.05))

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        plt.xticks(rotation=45)
        
        plt.yticks([1, 2, 3], ["나빠요", "보통이에요", "좋아요"])
        plt.xlabel('Time')
        plt.ylabel('Event')
        plt.title('Symptom and Medication Over Time')
        plt.legend()
        plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return 'data:image/png;base64,{}'.format(graph_url)


def create_interactive_graph(df):
    """ Create an interactive graph from the DataFrame using Plotly """
    if df.empty:
        return None

    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')
    events = {"좋아요": 1, "보통이에요": 2, "나빠요": 3}
    df['event_num'] = df['event'].map(events)

    trace_symptoms = go.Scatter(
        x=df[df['type'] == 'symptom']['time'],
        y=df[df['type'] == 'symptom']['event_num'],
        mode='lines+markers',
        name='Symptoms',
        marker=dict(color='blue')
    )

    trace_medications = go.Scatter(
        x=df[df['type'] == 'medication']['time'],
        y=df[df['type'] == 'medication']['event_num'],
        mode='markers',
        name='Medications',
        marker=dict(color='red', symbol='triangle-up')
    )

    layout = go.Layout(
        title='Symptom and Medication Over Time',
        xaxis=dict(title='Time'),
        yaxis=dict(
            title='Event',
            tickvals=[1, 2, 3],
            ticktext=["좋아요", "보통이에요", "나빠요"]
        ),
        height=600,
        width=1000
    )

    fig = go.Figure(data=[trace_symptoms, trace_medications], layout=layout)

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html