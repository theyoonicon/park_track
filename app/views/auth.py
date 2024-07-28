from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for, make_response, session
from ..models import User
from .. import db, bcrypt
from flask_jwt_extended import JWTManager, set_access_cookies, unset_jwt_cookies, create_access_token, decode_token, jwt_required, get_jwt_identity, get_jwt
import functools

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        if data is None:
            data = request.form
        username = data.get('username')
        password = data.get('password')
        print("username:", username, "password", password)
        if not username or not password:
            flash("Missing username or password")
            return render_template('register.html')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("User already exists")
            return render_template('register.html')
            # return jsonify({"message": "User already exists"}), 400
        new_user = User(username=username, password=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"message": "Register successful"}), 201
        flash("User registered successfully")
        return redirect(url_for('auth.login'))
    else:
        return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        if data is None:
            data = request.form
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id)
            response = make_response(redirect(url_for('home.home')))
            set_access_cookies(response, access_token)
            session['logged_in'] = True
            session['user_id'] = user.id
            return response
        flash("Invalid credentials")
        return render_template('login.html')
    else:
        return render_template('login.html')

def get_jwt_identity_from_request():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        token = request.cookies.get('access_token')
    if not token:
        return None
    try:
        decoded_token = decode_token(token)
        return decoded_token['sub']
    except Exception as e:
        return None

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    response = redirect(url_for('auth.login'))
    unset_jwt_cookies(response)
    return response