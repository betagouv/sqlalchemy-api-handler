import pytest

from api.models.offer import Offer
from api.models.stock import Stock
from api.models.user import User


class AccessorTest:
    def test_get_with_a_string_path(self, app):
        # Given
        offer = Offer(name='foo', type='bar')
        stock = Stock(offer=offer, price=1)

        # When
        offer_name = stock.get('offer.name')

        # Then
        assert offer_name == offer.name

    def test_get_with_a_index_path(self, app):
        # Given
        offer = Offer(name='foo', type='bar')
        stock = Stock(offer=offer, price=1)

        # When
        stock_price = stock.get('offer.stocks.0.price')

        # Then
        assert stock_price == stock.price
