from flask import current_app
from flask_mail import Mail, Message
import functools
from itsdangerous import URLSafeTimedSerializer
from .. import db, bcrypt, mail

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
    except:
        return False
    return email

def send_email(to, subject, template):
    msg = Message(subject, recipients=[to], html=template, sender=current_app.config['MAIL_DEFAULT_SENDER'])
    mail.send(msg)