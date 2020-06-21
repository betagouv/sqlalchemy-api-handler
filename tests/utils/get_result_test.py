import pytest
from sqlalchemy_api_handler import ApiErrors, ApiHandler, humanize, get_result

from tests.conftest import with_clean
from tests.test_utils.models.offer import Offer
from tests.test_utils.models.stock import Stock

class GetResultTest:
    @with_clean
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
        result = get_result(Stock)
        data = result['data']

        # Then
        assert data[0]['id'] == humanize(stock2.id)
        assert data[1]['id'] == humanize(stock3.id)
        assert data[2]['id'] == humanize(stock4.id)

    @with_clean
    def test_check_order_by(self, app):
        # When
        with pytest.raises(ApiErrors) as e:
            get_result(Stock, order_by='(SELECT * FROM "user")')

        # Then
        assert 'order_by' in e.value.errors

    @with_clean
    def test_returns_total_data_count_with_has_more(self, app):
        # Given
        offer = Offer(name="foo", type="ThingType.JEUX_ABO")
        ApiHandler.save(offer)
        page = 2
        paginate = 10
        prices_length = 35
        stocks = []
        for price in range(prices_length):
            stock = Stock(price=price)
            stock.offer = offer
            stocks.append(stock)
        ApiHandler.save(*stocks)

        # When
        result = get_result(
            Stock,
            page=page,
            paginate=paginate,
            with_total_data_count=True
        )

        # Then
        assert len(result['data']) == paginate
        assert result['has_more'] == True
        assert result['total_data_count'] == prices_length

    @with_clean
    def test_returns_total_data_count_with_has_more(self, app):
        # Given
        offer = Offer(name="foo", type="ThingType.JEUX_ABO")
        ApiHandler.save(offer)
        page = 4
        paginate = 10
        prices_length = 35
        stocks = []
        for price in range(prices_length):
            stock = Stock(price=price)
            stock.offer = offer
            stocks.append(stock)
        ApiHandler.save(*stocks)

        # When
        result = get_result(
            Stock,
            page=page,
            paginate=paginate,
            with_total_data_count=True
        )

        # Then
        assert len(result['data']) == page * paginate - prices_length 
        assert result['has_more'] == False
        assert result['total_data_count'] == prices_length
