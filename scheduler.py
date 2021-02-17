from celery.schedules import crontab
from functools import reduce
from flask import Flask

from api.tasks import import_tasks
from api.utils.celery import CELERY_APP
from api.utils.database import db
from api.utils.setup import setup


FLASK_APP = Flask(__name__)

setup(FLASK_APP)

import_tasks()


CELERY_APP.conf.beat_schedule = {
    'hourly_hello_sync': {
        'kwargs': {
            'mode': 'Karl !'
        },
        'task': 'tasks.hello.print_text',
        'schedule': crontab(minute=15, hour='*/1'),
    },
}

CELERY_APP.conf.timezone = 'UTC'

db.session.close()
