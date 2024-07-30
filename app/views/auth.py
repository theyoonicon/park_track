from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for, make_response, session
from ..models import User
from .. import db, bcrypt
from flask_jwt_extended import JWTManager, set_access_cookies, unset_jwt_cookies, create_access_token, decode_token, jwt_required, get_jwt_identity, get_jwt
import functools
from datetime import datetime
from .email import generate_confirmation_token, send_email, confirm_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        if data is None:
            data = request.form
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        print("username:", username, "password", password, "email", email)
        if not username or not password or not email:
            flash("Missing username, password or email")
            return render_template('register.html')
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("User already exists")
            return render_template('register.html')
            # return jsonify({"message": "User already exists"}), 400
        new_user = User(username=username, password=bcrypt.generate_password_hash(password).decode('utf-8'), email=email)
        db.session.add(new_user)
        db.session.commit()
        
        token = generate_confirmation_token(email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(email, subject, html)
        
        ### 모바일 register 는 막음
        #if request.headers.get('Accept') == 'application/json':
        #    return jsonify({"message": "Register successful"}), 201
        #flash("User registered successfully")
        
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('auth.login'))
        
    else:
        return render_template('register.html')
    
@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('auth.login'))


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
            if request.headers.get('Accept') == 'application/json':
                    return jsonify({"message": "Login successful", "token": access_token}), 200
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

@auth_bp.route('/logout')
def logout():
    if request.headers.get('Accept') == 'application/json':
        print("come")
        # response = make_response(jsonify({"message": "Logged out successfully"}), 200)
        # response.delete_cookie('access_token')
        return jsonify({"message": "log-out"}), 200
    session.clear()
    response = redirect(url_for('auth.login'))
    unset_jwt_cookies(response)
    return response