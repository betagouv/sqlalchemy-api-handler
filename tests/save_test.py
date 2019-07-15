import pytest
from sqlalchemy import Column, Text

from sqlalchemy_manager import Manager, Model

class User(Manager, Model):
    name = Column(Text)

class SaveTest:
    def test_save_user(self):
        # Given
        user = User(name="Marx Foo")

        # When
        Manager.save(user)
