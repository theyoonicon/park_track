from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jti, get_jwt, jwt_required
import os
from flask_login import current_user, LoginManager

db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    config_name = os.getenv('FLASK_CONFIG', 'default')
    print(config_name)
    if config_name == 'development':
        app.config.from_object('config.development.DevelopmentConfig')
    elif config_name == 'production':
        app.config.from_object('config.production.ProductionConfig')
    else:
        app.config.from_object('config.default.Config')

    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    from .models import User  # User 모델을 임포트
    
    from .views.auth import auth_bp
    from .views.symptoms import symptoms_bp
    from .views.home import home_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(symptoms_bp)
    app.register_blueprint(home_bp)


    with app.app_context():
        db.create_all()  # 데이터베이스 테이블 생성

    return app
