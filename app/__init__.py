from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    config_name = os.getenv('FLASK_CONFIG', 'default')
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

    from .views.auth import auth_bp
    from .views.symptoms import symptoms_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(symptoms_bp)

    with app.app_context():
        db.create_all()  # 데이터베이스 테이블 생성

    return app
