from sqlalchemy import Column, Text, String
from sqlalchemy_api_handler import ApiHandler

from tests.test_utils.db import Model

class User(ApiHandler, Model):
    firstName = Column(String(128), nullable=True)

    email = Column(String(120), nullable=False, unique=True)

    lastName = Column(String(128), nullable=True)

    postalCode = Column(String(5), nullable=True)

    publicName = Column(String(255), nullable=False)
