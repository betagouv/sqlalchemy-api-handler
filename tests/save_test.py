import pytest

from sqlalchemy_manager import Manager, Model
from tests.utils.user import User

class SaveTest():
    def test_save_user(self, app):
        # Given
        user = User(name="Marx Foo")

        # When
        Manager.save(user)
