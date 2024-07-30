import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you_will_never_guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # 토큰 만료 시간 설정
    REMEMBER_COOKIE_DURATION = timedelta(days=1)
    SECURITY_PASSWORD_SALT = 'your_security_password_salt'
    MAIL_DEFAULT_SENDER = 'zzangnyun@gmail.com'
    
    # Flask-Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'zzangnyun@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'rcbq sbet ozof qqxu')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'zzangnyun@gmail.com')