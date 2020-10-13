from sqlalchemy import BigInteger, \
                       Column, \
                       ForeignKey
from postgresql_audit.flask import versioning_manager
from sqlalchemy.orm import relationship
from sqlalchemy_api_handler import ApiHandler, \
                                   ActivityMixin

from tests.test_utils.database import db


versioning_manager.init(db.Model)


class Activity(ApiHandler,
               versioning_manager.activity_cls,
               ActivityMixin):
    __table_args__ = {'extend_existing': True}

    id = versioning_manager.activity_cls.id

    #userId = Column(BigInteger(),
    #                ForeignKey('user.user_id'))

    #user = relationship('User',
    #                    foreign_keys=[userId],
    #                    backref='activities')
