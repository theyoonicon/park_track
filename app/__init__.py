from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jti, get_jwt, jwt_required
from flask_mail import Mail
from flask_migrate import Migrate
from sqlalchemy import MetaData
import os
from flask_login import current_user, LoginManager


# Naming convention for SQLAlchemy constraints
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
ma = Marshmallow()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()
migrate = Migrate()


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
    mail.init_app(app)
    migrate.init_app(app, db)
    
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
