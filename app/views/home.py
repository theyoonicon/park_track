from flask import Blueprint, render_template, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required
from ..models import User
from .auth import get_jwt_identity_from_request

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@home_bp.route('/home', methods=['GET'])
@jwt_required(optional=True)
def home():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized access"}), 401
    user = User.query.get(user_id)
    if user:
        return render_template('home.html', username=user.username)
    return jsonify({"message": "Unauthorized access"}), 401
