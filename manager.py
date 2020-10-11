from flask import Flask
from flask_script import Manager

from commands import import_commands
from utils.setup import setup


FLASK_APP = Flask(__name__)

setup(FLASK_APP)

def create_app(env=None):
    FLASK_APP.env = env
    return FLASK_APP

FLASK_APP.manager = Manager(create_app)

import_commands()

if __name__ == '__main__':
    FLASK_APP.manager.run()
