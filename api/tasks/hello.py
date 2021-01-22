from sqlalchemy_api_handler import ApiHandler

from api.utils.celery import CELERY_APP


@CELERY_APP.task
def print_text(text):
    print(f'Hello {text}')
    return { 'text': text }
