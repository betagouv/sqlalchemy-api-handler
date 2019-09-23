import pytest
from sqlalchemy_api_handler import ApiErrors, ApiHandler, humanize, listify

from tests.conftest import clean_database
from tests.test_utils.models.offer import Offer
from tests.test_utils.models.stock import Stock

class ListifyTest:
    @clean_database
    def test_return_only_not_soft_deleted_stocks(self, app):
        # Given
        offer = Offer(name="foo", type="ThingType.JEUX_ABO")
        ApiHandler.save(offer)
        stock1 = Stock(price=1)
        stock1.offer = offer
        stock2 = Stock(price=2)
        stock2.offer = offer
        stock3 = Stock(price=3)
        stock3.offer = offer
        stock4 = Stock(price=4)
        stock4.offer = offer
        stock1.isSoftDeleted = True
        ApiHandler.save(stock1, stock2, stock3, stock4)

        # When
        elements = listify(Stock)

        # Then
        assert elements[0]['id'] == humanize(stock2.id)
        assert elements[1]['id'] == humanize(stock3.id)
        assert elements[2]['id'] == humanize(stock4.id)

    @clean_database
    def test_check_order_by(self, app):
        # When
        with pytest.raises(ApiErrors) as e:
            listify(Stock, order_by='(SELECT * FROM "user")')

        # Then
        assert 'order_by' in e.value.errors
