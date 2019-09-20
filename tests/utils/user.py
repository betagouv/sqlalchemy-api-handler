from sqlalchemy import Column, Text

from tests.utils.db import Model
from sqlalchemy_handler import Handler

class User(Handler, Model):
    name = Column(Text)
