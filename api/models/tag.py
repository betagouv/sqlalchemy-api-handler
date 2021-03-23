import enum
import time
from sqlalchemy import Column, String, Text
from sqlalchemy_api_handler import ApiHandler

from api.utils.database import db


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

    @property
    def sleptFoo(self):
        time.sleep(0.5)
        return 0

    __as_dict_includes__ = ['sleptFoo']
