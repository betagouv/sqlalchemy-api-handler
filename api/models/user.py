from sqlalchemy import BigInteger, Column, Text, String
from sqlalchemy.orm import synonym
from sqlalchemy_api_handler import ApiHandler

from api.utils.database import db


class User(ApiHandler,
           db.Model):

    email = Column(String(120),
                   nullable=False,
                   unique=True)

    firstName = Column(String(128),
                       nullable=True)

    lastName = Column(String(128),
                      nullable=True)

    metier = Column(String(128))

    postalCode = Column(String(5),
                        nullable=True)

    publicName = Column(String(255),
                        nullable=False)

    job = synonym('metier')

    user_id = Column(BigInteger(),
                     autoincrement=True,
                     primary_key=True)

    id = synonym('user_id')

    def get_id(self):
        return str(self.id)

    # necessary for flask login…
    def is_active(self):
        return self.isActive

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    __as_dict_includes__ = [
        '-metier',
        '-user_id',
        'id',
        'job'
    ]
