import enum
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy_api_handler import ApiHandler

from tests.test_utils.db import Model


class TagType(enum.Enum):
    CONCLUSION = 'conclusion'
    DETAIL = 'detail'
    EVALUATION = 'evaluation'
    ISSUE = 'issue'
    QUALIFICATION = 'qualification'


class Tag(ApiHandler,
          Model):

    info = Column(Text())

    label = Column(String(128), unique=True)

    value = Column(Integer())
