from flask import Blueprint, flash, request, jsonify, render_template, redirect, url_for, make_response, session
from ..models import User
from .. import db, bcrypt
from flask_jwt_extended import JWTManager, set_access_cookies, unset_jwt_cookies, create_access_token, decode_token, jwt_required, get_jwt_identity, get_jwt
import functools
from datetime import datetime
from .email import generate_confirmation_token, send_email, confirm_token
import os, pickle
from .forms import RegistrationForm

auth_bp = Blueprint('auth', __name__)

def save_temp_user(data):
    with open(f'temp_user_{data["email"]}.pkl', 'wb') as f:
        pickle.dump(data, f)

def load_temp_user(email):
    try:
        with open(f'temp_user_{email}.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def delete_temp_user(email):
    try:
        os.remove(f'temp_user_{email}.pkl')
    except FileNotFoundError:
        pass

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            form = RegistrationForm(data=data)
        else:
            form = RegistrationForm()
        
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            email = form.email.data
            print("username:", username, "password", password, "email:", email)
            if not username or not password or not email:
                if request.is_json:
                    return jsonify({"message": "Missing username, password, or email"}), 400
                else:
                    flash("Missing username, password, or email")
                    return render_template('register.html', form=form)
            
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                if request.is_json:
                    return jsonify({"message": "User with that username or email already exists"}), 400
                else:
                    flash("User with that username or email already exists")
                    return render_template('register.html', form=form)

            temp_user = {
                'username': username,
                'password': bcrypt.generate_password_hash(password).decode('utf-8'),
                'email': email
            }
            save_temp_user(temp_user)

            token = generate_confirmation_token(email)
            confirm_url = url_for('auth.confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(email, subject, html)

            if request.is_json:
                return jsonify({"message": "A confirmation email has been sent via email."}), 201
            else:
                flash('A confirmation email has been sent via email.', 'success')
                return redirect(url_for('auth.login'))
        
        if request.is_json:
            return jsonify({"errors": form.errors}), 400

    return render_template('register.html', form=form)

    
@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    temp_user = load_temp_user(email)
    if not temp_user:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.register'))

    user = User.query.filter_by(email=email).first()
    if user:
        flash('Account already confirmed. Please login.', 'success')
    else:
        new_user = User(
            username=temp_user['username'],
            password=temp_user['password'],
            email=temp_user['email'],
        )
        new_user.confirmed=True
        new_user.confirmed_on=datetime.utcnow()
        db.session.add(new_user)
        db.session.commit()
        delete_temp_user(email)
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