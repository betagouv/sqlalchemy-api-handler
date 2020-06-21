import enum
from sqlalchemy import BigInteger, \
                       Column, \
                       Enum, \
                       ForeignKey, \
                       String
from sqlalchemy.orm import relationship
from sqlalchemy_api_handler import ApiHandler

from tests.test_utils.db import Model


class ScopeType(enum.Enum):
    CLAIM = 'claim'
    CONTENT = 'content'
    REVIEW = 'review'
    USER = 'user'
    VERDICT = 'verdict'


class Scope(ApiHandler,
            Model):

    tagId = Column(BigInteger(),
                   ForeignKey('tag.id'),
                   nullable=False,
                   index=True)

    tag = relationship('Tag',
                       foreign_keys=[tagId],
                       backref='scopes')

    type = Column(Enum(ScopeType))
