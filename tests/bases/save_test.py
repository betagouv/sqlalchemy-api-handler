import pytest
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.utils.human_ids import dehumanize, NonDehumanizableId

from tests.test_utils.db import Model
from tests.test_utils.models.offer import Offer
from tests.test_utils.models.stock import Stock


class SaveTest:
    def test_for_valid_relationship(self):
        # Given
        offer = Offer(name="foo", type="bar")
        stock = Stock(offer=offer, price=1)

        # When
        ApiHandler.save(stock)

        # Then
        assert stock.offerId == offer.id
