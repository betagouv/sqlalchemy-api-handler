import os

APP_NAME = os.environ.get('APP_NAME', '')
COMMAND_NAME = os.environ.get('COMMAND_NAME', '')
PORT = int(os.environ.get('PORT', 5000))
API_URL = 'http://api:{}'.format(PORT)
