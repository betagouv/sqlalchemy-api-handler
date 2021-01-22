import os
import celery

from api.utils.config import APP_NAME


CELERY_TASKS_LIMIT = int(os.environ.get('CELERY_TASKS_LIMIT') or 10)
LOCALHOST_REDIS_URL = f'redis://apiredisdb:6379/0'
REDIS_URL = os.environ.get('REDIS_URL', LOCALHOST_REDIS_URL)


CELERY_APP = celery.Celery('{}-tasks'.format(APP_NAME),
                           backend=REDIS_URL,
                           broker=REDIS_URL,
                           broker_pool_limit=CELERY_TASKS_LIMIT)
CELERY_APP.conf.task_default_queue = 'default'
CELERY_APP.is_disabled = False
