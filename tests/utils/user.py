from sqlalchemy import Column, Text

from sqlalchemy_handler import Handler, Model

class User(Handler, Model):
    name = Column(Text)
