from sqlalchemy import BigInteger, Column, Text, String
from sqlalchemy.orm import synonym
from sqlalchemy_api_handler import ApiHandler

from tests.test_utils.db import Model


class User(ApiHandler, Model):
    firstName = Column(String(128), nullable=True)

    email = Column(String(120), nullable=False, unique=True)

    lastName = Column(String(128), nullable=True)

    metier = Column(String(128))

    postalCode = Column(String(5), nullable=True)

    publicName = Column(String(255), nullable=False)

    job = synonym('metier')

    user_id = Column(BigInteger(), autoincrement=True, primary_key=True)

    id = synonym('user_id')

    __as_dict_includes__ = [
        '-metier',
        '-user_id',
        'id',
        'job'
    ]
