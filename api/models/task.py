from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.mixins import TaskMixin

from api.utils.database import db


class Task(ApiHandler,
            db.Model,
            TaskMixin):
    pass
