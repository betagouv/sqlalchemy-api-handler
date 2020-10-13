import enum
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy_api_handler import ApiHandler

from tests.api.database import db


class TagType(enum.Enum):
    CONCLUSION = 'conclusion'
    DETAIL = 'detail'
    EVALUATION = 'evaluation'
    ISSUE = 'issue'
    QUALIFICATION = 'qualification'


class Tag(ApiHandler,
          db.Model):

    info = Column(Text())

    label = Column(String(128), unique=True)

    value = Column(Integer())
