# -*- coding: utf-8 -*-
from flask import current_app as app
from flask.testing import FlaskClient
from flask_script import Command
from pprint import pprint
import requests
from requests.auth import _basic_auth_str

from utils.config import API_URL, \
                         COMMAND_NAME, \
                         DEFAULT_USER_PASSWORD, \
                         WEBAPP_URL


@app.manager.add_command
class RequestCommand(Command):
    __doc__ = ''' e.g. `{} request get /checks/user` pings the /checks/user api route'''.format(COMMAND_NAME)
    name = 'request'
    capture_all_args = True

    def run(self, args):
        headers = {
            'Authorization': _basic_auth_str('fbtest.master0@feedback.news',
                                             DEFAULT_USER_PASSWORD),
            'origin': WEBAPP_URL
        }
        method = args[0]
        url = '{}{}'.format(API_URL, args[1])
        response = getattr(requests, method)(url, headers=headers)
        if response.headers.get('content-type') == 'application/json':
            pprint(response.json())
        else:
            print(response.text)
