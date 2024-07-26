from config.default import Config
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
