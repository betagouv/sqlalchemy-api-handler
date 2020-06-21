import enum
from sqlalchemy import BigInteger, Column, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from sqlalchemy_api_handler import ApiHandler

from tests.test_utils.db import Model


class RightsType(enum.Enum):
    admin = "admin"
    editor = "editor"


class UserOfferer(ApiHandler, Model):

    userId = Column(BigInteger,
                    ForeignKey('user.user_id'),
                    primary_key=True)

    user = relationship('User',
                        foreign_keys=[userId],
                        backref=backref("UserOfferers"))

    offererId = Column(BigInteger,
                       ForeignKey('offerer.id'),
                       index=True,
                       primary_key=True)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref=backref("UserOfferers"))

    rights = Column(Enum(RightsType))

    __table_args__ = (
        UniqueConstraint(
            'userId',
            'offererId',
            name='unique_user_offerer',
            ),
        )
