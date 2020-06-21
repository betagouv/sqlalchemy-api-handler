import pytest

from sqlalchemy_api_handler import ApiHandler
from tests.conftest import with_clean
from tests.test_utils.models.user import User

class SaveTest():
    @with_clean
    def test_save_user(self, app):
        # given
        user = User(
            firstName="Marx",
            email="marx.foo@plop.fr",
            lastName="Foo",
            publicName="Marx Foo"
        )

        # when
        ApiHandler.save(user)

        # then
        saved_user = User.query.first()
        assert saved_user.firstName == "Marx"
