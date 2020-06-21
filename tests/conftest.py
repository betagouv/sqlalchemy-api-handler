from functools import wraps
from flask import Flask
import pytest

from tests.test_utils.db import clean, db
from tests.test_utils.setup import setup


@pytest.fixture(scope='session')
def app():
    FLASK_APP = Flask(__name__)
    setup(FLASK_APP)
    return FLASK_APP


def with_clean(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db.session.rollback()
        clean()
        return f(*args, **kwargs)

    return decorated_function
