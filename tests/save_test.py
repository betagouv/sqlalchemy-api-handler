import pytest

from sqlalchemy_handler import Handler, Model
from tests.utils.user import User

class SaveTest():
    def test_save_user(self, app):
        # Given
        user = User(name="Marx Foo")

        # When
        Handler.save(user)
