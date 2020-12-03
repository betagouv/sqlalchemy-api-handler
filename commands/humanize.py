from flask import current_app as app
from flask_script import Command
from sqlalchemy_api_handler.utils import humanize as h

from api.utils import COMMAND_NAME


@app.manager.add_command
class HumanizeCommand(Command):
    __doc__ = ''' e.g. `{} humanize 3` prints `AM`'''.format(COMMAND_NAME)
    name = 'humanize'
    capture_all_args = True

    def run(self, args):
        print(h(int(args[0])))
