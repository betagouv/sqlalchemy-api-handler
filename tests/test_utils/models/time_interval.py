from sqlalchemy import Column, DateTime
from sqlalchemy_api_handler import ApiHandler

from tests.test_utils.db import Model


class TimeInterval(ApiHandler, Model):
    start = Column(DateTime)
    end = Column(DateTime)
