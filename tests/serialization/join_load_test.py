import pytest
from ttictoc import tic,toc
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy.orm import joinedload
from sqlalchemy_api_handler.serialization import as_dict

from api.models.offer import Offer
from api.models.stock import Stock
from tests.conftest import with_delete


class JoinLoadTest:
    @with_delete
    def test_join_load(self, app):
        # given
        offer = Offer(name='foo', type='bar')
        stock = Stock(offer=offer, price=0)
        ApiHandler.save(stock)
        stock = Stock.query.filter_by(price=0) \
                           .options(joinedload(Stock.offer)) \
                           .first()

        # when
        tic()
        as_dict(stock, includes=['offer'])
        elapsed = toc()
        #tic()
        #print(as_dict(stock2, includes=['offer']))
        #elapsed2 = toc()

        # then
        assert elapsed == 3

    @with_delete
    def test_load(self, app):
        # given
        offer = Offer(name='foo', type='bar')
        stock = Stock(offer=offer, price=0)
        ApiHandler.save(stock)
        stock = Stock.query.filter_by(price=0) \
                       .options(joinedload(Stock.offer)) \
                       .first()

        # when
        tic()
        as_dict(stock, includes=['offer'])
        elapsed = toc()
        #tic()
        #print(as_dict(stock2, includes=['offer']))
        #elapsed2 = toc()

        # then
        assert elapsed == 3

    @with_delete
    def test_join_load1(self, app):
        # given
        offer = Offer(name='foo', type='bar')
        stock = Stock(offer=offer, price=0)
        ApiHandler.save(stock)
        stock = Stock.query.filter_by(price=0) \
                       .first()

        # when
        tic()
        as_dict(stock, includes=['offer'])
        elapsed = toc()
        #tic()
        #print(as_dict(stock2, includes=['offer']))
        #elapsed2 = toc()

        # then
        assert elapsed == 3

    @with_delete
    def test_join_load2(self, app):
        # given
        offer = Offer(name='foo', type='bar')
        stock = Stock(offer=offer, price=0)
        ApiHandler.save(stock)
        stock = Stock.query.filter_by(price=0) \
                       .first()

        # when
        tic()
        as_dict(stock, includes=['offer'])
        elapsed = toc()
        #tic()
        #print(as_dict(stock2, includes=['offer']))
        #elapsed2 = toc()

        # then
        assert elapsed == 3

    @with_delete
    def test_load666(self, app):
        # given
        offer = Offer(name='foo', type='bar')
        stock = Stock(offer=offer, price=0)
        ApiHandler.save(stock)
        stock = Stock.query.filter_by(price=0) \
                       .options(joinedload(Stock.offer)) \
                       .first()

        # when
        tic()
        as_dict(stock, includes=['offer'])
        elapsed = toc()
        #tic()
        #print(as_dict(stock2, includes=['offer']))
        #elapsed2 = toc()

        # then
        assert elapsed == 3
