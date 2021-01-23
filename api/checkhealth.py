# pylint: disable=W0611

import os
from time import sleep
from flask import Flask
from random import random
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.utils import logger
from sqlalchemy.exc import OperationalError

from api.repository.checks import check_from_model
from api.utils.config import VERSION
from api.utils.setup import setup
from api.utils.database import db


SLEEP_TIME = 1

FLASK_APP = Flask(__name__)


setup(FLASK_APP,
      with_cors=False)


TABLE_NAME = f'check_health_{int(1000*random())}'
class CheckHealth(db.Model, ApiHandler):
    __tablename__ = TABLE_NAME
    pass


def check_from_model(model):
    database_working = False
    version = 'Api {} : '.format(VERSION)
    try:
        model.query.limit(1).all()
        database_working = True
        state = 'database is ok.'
    except Exception as e:
        logger.critical(str(e))
        state = 'database is not ok.'
    output = '{}{}'.format(version, state)

    return database_working, output

IS_DATABASE_CONNECT_OK = False
while not IS_DATABASE_CONNECT_OK:
    try:
        CheckHealth.__table__.drop(db.session.bind, checkfirst=True)
        CheckHealth.__table__.create(db.session.bind)
        db.session.commit()
    except OperationalError:
        print('Could not connect to postgres db... Retry in {}s...'.format(SLEEP_TIME))
        sleep(SLEEP_TIME)
        continue
    print('Connection to postgres db is okay.')
    IS_DATABASE_CONNECT_OK = True

IS_DATABASE_HEALTH_OK = False
while not IS_DATABASE_HEALTH_OK:
    IS_DATABASE_HEALTH_OK = check_from_model(CheckHealth)[0]
    db.session.execute(f'DROP TABLE {TABLE_NAME};')
    db.session.commit()
    if not IS_DATABASE_HEALTH_OK:
        print('Could not check database health... Retry in {}s...'.format(SLEEP_TIME))
    else:
        print('Database health is ok.')
