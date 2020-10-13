from datetime import datetime

from sqlalchemy import Column, \
                       DateTime, \
                       String
from sqlalchemy.orm import relationship
from sqlalchemy_api_handler import ApiHandler

from tests.api.database import db


class Offerer(ApiHandler,
              db.Model):
    dateCreated = Column(DateTime,
                         default=datetime.utcnow,
                         nullable=False)

    name = Column(String(140),
                  nullable=False)

    siren = Column(String(9),
                   nullable=True,
                   unique=True)

    users = relationship('User',
                         secondary='user_offerer')
