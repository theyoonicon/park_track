from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# import config

db = SQLAlchemy()
migrate = Migrate()


from . import models

def create_app():
    app = Flask(__name__)
    # app.config.from_object(config)
    app.config.from_envvar('APP_CONFIG_FILE')
    
    # ORM
    db.init_app(app)
    migrate.init_app(app, db)


    # blueprint
    from .views import main_views, data_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(data_views.bp)

    return app

def main():
    app = create_app()
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()