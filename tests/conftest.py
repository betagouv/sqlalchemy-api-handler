import os
from datetime import datetime
from functools import wraps
from flask import Flask
import pytest

from sqlalchemy_manager import db
from tests.utils.install_models import install_models

@pytest.fixture(scope='session')
def app(request):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '@##&6cweafhv3426445'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL')

    print('URL', app.config['SQLALCHEMY_DATABASE_URI'])

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)

    app.app_context().push()
    print('OUI')
    install_models()

    return app

def clean_database(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db.session.rollback()
        clean_all_database()
        return f(*args, **kwargs)

    return decorated_function
