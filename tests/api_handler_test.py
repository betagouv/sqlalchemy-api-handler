import pytest

from sqlalchemy_api_handler import ApiHandler
from tests.conftest import with_delete
from api.models.user import User


class SaveTest():
    @with_delete
    def test_save_user(self, app):
        # given
        user_dict = {
            'email': 'marx.foo@plop.fr',
            'firstName': 'Marx',
            'lastName': 'Foo',
            'publicName': 'Marx Foo'
        }
        user = User(**user_dict)

        # when
        ApiHandler.save(user)

        # then
        saved_user = User.query.first()
        for (key, value) in user_dict.items():
            assert getattr(saved_user, key) == value
