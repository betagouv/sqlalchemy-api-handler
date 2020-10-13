from flask import current_app as app
from flask_script import Command
from sqlalchemy_api_handler import dehumanize as dh

from tests.api.config import COMMAND_NAME


@app.manager.add_command
class DehumanizeCommand(Command):
    __doc__ = ''' e.g. `{} dehumanize AM` prints `3`'''.format(COMMAND_NAME)
    name = 'dehumanize'
    capture_all_args = True

    def run(self, args):
        print(dh(args[0]))
