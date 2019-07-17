import os
from datetime import datetime
from functools import wraps
from flask import Flask
import pytest

from sqlalchemy_handler import db
from tests.utils.install_models import install_models

@pytest.fixture(scope='session')
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '@##&6cweafhv3426445'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)

    app.app_context().push()
    install_models()

    return app
