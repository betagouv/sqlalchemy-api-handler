import pytest
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.utils.human_ids import dehumanize, NonDehumanizableId

from tests.conftest import clean_database
from tests.test_utils.db import Model
from tests.test_utils.models.offer import Offer
from tests.test_utils.models.offerer import Offerer
from tests.test_utils.models.stock import Stock
from tests.test_utils.models.user import User
from tests.test_utils.models.user_offerer import UserOfferer


class SaveTest:
    @clean_database
    def test_for_valid_one_to_many_relationship(self):
        # Given
        offer = Offer(name="foo", type="bar")
        stock = Stock(offer=offer, price=1)

        # When
        ApiHandler.save(stock)

        # Then
        assert stock.offerId == offer.id

    @clean_database
    def test_for_valid_many_to_many_relationship(self):
        # Given
        offerer = Offerer(name="foo", type="bar")
        user = User(email="bar@gmare.com", publicName="bar")
        ApiHandler.save(user, offerer)
        user_offerer = UserOfferer(offerer=offerer, user=user)

        # When
        ApiHandler.save(user_offerer)

        # Then
        assert user_offerer.offererId == offerer.id
        assert user_offerer.userId == user.id
