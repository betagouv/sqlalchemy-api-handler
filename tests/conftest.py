from functools import wraps
from flask import Flask
import pytest

from api.utils.database import create, db, delete
from api.utils.setup import setup


@pytest.fixture(scope='session')
def app():
    FLASK_APP = Flask(__name__)

    setup(FLASK_APP,
          with_login_manager=True)

    try:
        create()
    except Exception:
        pass
    return FLASK_APP


def with_delete(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db.session.rollback()
        delete()
        return f(*args, **kwargs)
    return decorated_function
