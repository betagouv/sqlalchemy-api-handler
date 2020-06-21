import os
from sqlalchemy_api_handler import ApiHandler
from tests.test_utils.db import db
from tests.test_utils.models import import_models


def setup(flask_app):
    flask_app.config['SECRET_KEY'] = '@##&6cweafhv3426445'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL')
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['TESTING'] = True

    db.init_app(flask_app)
    ApiHandler.set_db(db)

    flask_app.app_context().push()
    import_models()
