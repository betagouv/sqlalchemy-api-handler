import pytest
from sqlalchemy_api_handler.bases.errors import GetPathError

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

    def test_get_with_an_index_path_at_entity(self, app):
        # Given
        offer = Offer(name='foo', type='bar')
        stock1 = Stock(offer=offer, price=1)

        # When
        stock2 = stock1.get('offer.stocks.0')

        # Then
        assert stock1.id == stock2.id


    def test_get_with_an_index_path_at_value(self, app):
        # Given
        offer = Offer(name='foo', type='bar')
        stock = Stock(offer=offer, price=1)

        # When
        stock_price = stock.get('offer.stocks.0.price')

        # Then
        assert stock_price == stock.price

    def test_get_with_a_failing_empty_path(self, app):
        # Given
        stock = Stock(price=1)

        # When
        with pytest.raises(GetPathError):
            offer_name = stock.get('offer.name')

    def test_get_with_a_silent_empty_path_return(self, app):
        # Given
        stock = Stock(price=1)

        # When
        offer_name = stock.get('offer.name', with_get_path_error=False)

        # Then
        assert offer_name == None
