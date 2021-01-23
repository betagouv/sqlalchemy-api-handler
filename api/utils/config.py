import os
import sys

APP_NAME = os.environ.get('APP_NAME', '')
COMMAND_NAME = os.environ.get('COMMAND_NAME', '')
PORT = int(os.environ.get('PORT', 5000))
API_URL = 'http://api:{}'.format(PORT)

IS_SCHEDULER = sys.argv[0].endswith('celery') \
               and len(sys.argv) > 3 and \
               sys.argv[2] == 'beat'
IS_WORKER = sys.argv[0].endswith('celery') \
            and len(sys.argv) > 3 \
            and sys.argv[2] == 'worker'
IS_APP = not IS_SCHEDULER and not IS_WORKER
