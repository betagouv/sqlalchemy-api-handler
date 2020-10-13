from sqlalchemy import Column, DateTime
from sqlalchemy_api_handler import ApiHandler

from tests.api.database import db


class TimeInterval(ApiHandler,
                   db.Model):

    end = Column(DateTime)

    start = Column(DateTime)
