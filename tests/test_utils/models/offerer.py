from datetime import datetime

from sqlalchemy import Column, \
                       DateTime, \
                       String
from sqlalchemy.orm import relationship
from sqlalchemy_api_handler import ApiHandler

from tests.test_utils.db import Model


class Offerer(ApiHandler,
              Model):
    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    name = Column(String(140), nullable=False)

    siren = Column(String(9),
                   nullable=True,
                   unique=True)

    users = relationship('User',
                         secondary='user_offerer')
