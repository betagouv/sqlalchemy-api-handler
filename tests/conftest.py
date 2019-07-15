from datetime import datetime
from functools import wraps
from flask import Flask
import pytest

import sqlalchemy_manager as sam
from sqlalchemy_manager import db

@pytest.fixture
def app(request):
    app = Flask(request.module.__name__)
    db.init_app(app)
    app.testing = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app

def clean_database(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db.session.rollback()
        clean_all_database()
        return f(*args, **kwargs)

    return decorated_function
