from flask_login import LoginManager
from sqlalchemy_api_handler import ApiHandler

from api.models import import_models
from api.utils.config import IS_APP, \
                             IS_WORKER
from api.utils.database import POSTGRES_URL, db


def setup(flask_app,
          with_login_manager=False):
    flask_app.config['SECRET_KEY'] = '@##&6cweafhv3426445'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URL
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['TESTING'] = True

    db.init_app(flask_app)

    @flask_app.teardown_request
    def remove_db_session(exc):
        try:
            db.session.remove()
        except AttributeError:
            pass

    flask_app.app_context().push()
    import_models()

    if with_login_manager:
        from flask_login import LoginManager
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

    if IS_APP or IS_WORKER:
        from api.utils.celery import CELERY_APP
        ApiHandler.set_celery(CELERY_APP, flask_app)
