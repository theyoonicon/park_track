from flask import Blueprint, render_template, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User
from .auth import get_jwt_identity_from_request

home_bp = Blueprint('home', __name__)

# 새로운 선택 화면 엔드포인트 추가
@home_bp.route('/<username>/home', methods=['GET'])
@jwt_required(optional=True)
def home(username):
    user_id = get_jwt_identity_from_request()
    if not user_id:
        return jsonify({"message": "Unauthorized access"}), 401
    user = User.query.get(user_id)
    if user and user.username == username:
        return render_template('home.html', username=username)
    return jsonify({"message": "Unauthorized access"}), 401