from sqlalchemy import BigInteger, Column, Text, String
from sqlalchemy.orm import synonym
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.mixins import HasActivitiesMixin

from api.utils.database import db


class User(ApiHandler,
           db.Model,
           HasActivitiesMixin):

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

    def populate_from_dict(self, dct):
        user_dict = dict({}, **dct)

        password = None
        if dct.__contains__('password') and dct['password']:
            password = dct['password']
            del user_dict['password']

        super(User, self).populate_from_dict(user_dict)

        if password:
            self.set_password(password)

    def set_password(self, password, check=True):
        if check:
            self.clearTextPassword = password
        self.password = hashed_salted_password_from(password)

    __as_dict_includes__ = [
        '-metier',
        '-user_id',
        'id',
        'job'
    ]
