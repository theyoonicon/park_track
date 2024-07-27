from .default import Config
import os
from datetime import timedelta

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'production.db')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # 토큰 만료 시간 설정
