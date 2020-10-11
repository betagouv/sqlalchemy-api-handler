# pylint: disable=W0122

from flask import current_app as app
from flask_script import Command

from utils.config import COMMAND_NAME


@app.manager.add_command
class DevCommand(Command):
    __doc__ = ''' e.g. `{} dev foo.py` executes the files foo.py at api dir'''.format(COMMAND_NAME)
    name = 'dev'
    capture_all_args = True

    def run(self, args):
        file_path = '{}{}'.format('/opt/api/', args[0])
        kwargs = {}
        if len(args) > 1:
            kwargs['argv'] = args[1:]
        exec(open(file_path).read(), kwargs)
