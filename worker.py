from flask import Flask

from api.tasks import import_tasks
from api.utils.celery import CELERY_APP
from api.utils.setup import setup


FLASK_APP = Flask(__name__)

setup(FLASK_APP)

import_tasks()
