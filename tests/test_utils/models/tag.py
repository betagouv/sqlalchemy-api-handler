from sqlalchemy import Column, Integer, String, Text
from sqlalchemy_api_handler import ApiHandler

from tests.test_utils.db import Model


class Tag(ApiHandler,
          Model):

    evaluationValue = Column(Integer())

    label = Column(String(128), unique=True)

    info = Column(Text())
