import os
from flask_login import LoginManager
from sqlalchemy_api_handler import ApiHandler


from api.models import import_models
from api.utils.database import db


def setup(flask_app):
    flask_app.config['SECRET_KEY'] = '@##&6cweafhv3426445'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL')
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['TESTING'] = True

    db.init_app(flask_app)
    ApiHandler.set_db(db)

    flask_app.app_context().push()
    import_models()

    flask_app.config['SESSION_COOKIE_HTTPONLY'] = not flask_app.config['TESTING']
    flask_app.config['SESSION_COOKIE_SECURE'] = False
    flask_app.config['REMEMBER_COOKIE_HTTPONLY'] = not flask_app.config['TESTING']
    if not flask_app.config['TESTING']:
        flask_app.config['PERMANENT_SESSION_LIFETIME'] = 90 * 24 * 3600
        flask_app.config['REMEMBER_COOKIE_DURATION'] = 90 * 24 * 3600
        flask_app.config['REMEMBER_COOKIE_SECURE'] = True
    login_manager = LoginManager()
    login_manager.init_app(flask_app)
    import api.utils.login_manager
