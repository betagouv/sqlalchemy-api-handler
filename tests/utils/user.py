from sqlalchemy import Column, Text

from sqlalchemy_manager import Manager, Model

class User(Manager, Model):
    name = Column(Text)
