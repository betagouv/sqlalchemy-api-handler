import os
from functools import wraps
from flask import Flask
import pytest

from sqlalchemy_api_handler import ApiHandler
from tests.test_utils.db import db
from tests.test_utils.models.offer import Offer
from tests.test_utils.models.stock import Stock
from tests.test_utils.models.user import User
from tests.test_utils.install_models import install_models

@pytest.fixture(scope='session')
def app():
    flask_app = Flask(__name__)
    flask_app.config['SECRET_KEY'] = '@##&6cweafhv3426445'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL')
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['TESTING'] = True
    db.init_app(flask_app)
    ApiHandler.set_db(db)
    flask_app.app_context().push()
    install_models()

    return flask_app

def clean_database(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db.session.rollback()
        Stock.query.delete()
        Offer.query.delete()
        User.query.delete()
        db.session.commit()
        return f(*args, **kwargs)

    return decorated_function
