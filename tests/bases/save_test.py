import pytest
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.serialization import as_dict
from sqlalchemy_api_handler.utils import dehumanize, \
                                         humanize, \
                                         NonDehumanizableId

from tests.conftest import with_delete
from api.models.offer import Offer
from api.models.offerer import Offerer
from api.models.stock import Stock
from api.models.user import User
from api.models.user_offerer import UserOfferer


class SaveTest:
    @with_delete
    def test_for_valid_one_to_many_relationship(self, app):
        # Given
        offer = Offer(name='foo', type='bar')
        stock = Stock(offer=offer, price=1)

        # When
        ApiHandler.save(stock)

        # Then
        assert stock.offerId == offer.id

    @with_delete
    def test_for_valid_many_to_many_relationship(self, app):
        # Given
        offerer = Offerer(name='foo', type='bar')
        user = User(email='bar@gmare.com', publicName='bar')
        ApiHandler.save(user, offerer)
        user_offerer = UserOfferer(offerer=offerer, user=user)

        # When
        ApiHandler.save(user_offerer)

        # Then
        assert user_offerer.offererId == offerer.id
        assert user_offerer.userId == user.id

    @with_delete
    def test_for_valid_synonym(self, app):
        # Given
        job = 'foo'
        user = User(email='bar@gmare.com',
                    job=job,
                    publicName='bar')

        # When
        ApiHandler.save(user)

        # Then
        assert user.metier == job
        assert user.job == job

    @with_delete
    def test_for_valid_id_humanized_synonym(self, app):
        # Given
        user = User(email='bar@gmare.com',
                    publicName='bar')

        # When
        ApiHandler.save(user)

        # Then
        user_dict = as_dict(user)
        humanized_id = humanize(user.user_id)
        assert user_dict['id'] == humanized_id

    @with_delete
    def test_for_valid_relationship(self, app):
        # Given
        offer_dict = {
            'name': 'foo',
            'type': 'bar'
        }
        offer = Offer(**offer_dict)
        ApiHandler.save(offer)
        stock_dict = {
            'offer': offer,
            'price': 1
        }
        stock = Stock(**stock_dict)

        # When
        ApiHandler.save(stock)

        # Then
        assert stock.price == stock_dict['price']
        assert stock.offer.id == offer.id
        assert stock.offer.name == offer_dict['name']

    @with_delete
    def test_for_valid_relationships(self, app):
        # Given
        stock_dict1 = {
            'price': 1
        }
        stock1 = Stock(**stock_dict1)
        stock_dict2 = {
            'price': 2
        }
        stock2 = Stock(**stock_dict2)
        offer_dict = {
            'name': 'foo',
            'stocks': [stock1, stock2],
            'type': 'bar'
        }
        offer = Offer(**offer_dict)

        # When
        ApiHandler.save(offer)

        # Then
        assert offer.name == offer_dict['name']
        offer_stock1 = [s for s in offer.stocks if s.id == stock1.id][0]
        offer_stock2 = [s for s in offer.stocks if s.id == stock2.id][0]
        assert offer_stock1.price == stock1.price
        assert offer_stock2.price == stock2.price

    @with_delete
    def test_for_valid_relationship_dict_with_nested_creation(self, app):
        # Given
        offer_dict = {
            'name': 'foo',
            'type': 'bar'
        }
        stock_dict = {
            'offer': offer_dict,
            'price': 1
        }
        stock = Stock(**stock_dict)

        # When
        ApiHandler.save(stock)

        # Then
        assert stock.price == stock_dict['price']
        assert stock.offer.name == offer_dict['name']

    @with_delete
    def test_for_valid_relationship_dict_with_nested_modification(self, app):
        # Given
        offer_dict = {
            'name': 'foo',
            'type': 'bar'
        }
        offer = Offer(**offer_dict)
        ApiHandler.save(offer)
        offer_dict['id'] = humanize(offer.id)
        offer_dict['name'] = 'fooo'
        stock_dict = {
            'offer': offer_dict,
            'price': 1
        }
        stock = Stock(**stock_dict)

        # When
        ApiHandler.save(stock)

        # Then
        assert stock.price == stock_dict['price']
        assert stock.offer.id == offer.id
        assert stock.offer.name == offer_dict['name']

    @with_delete
    def test_for_valid_relationship_dicts_with_nested_creations(self, app):
        # Given
        stock_dict1 = {
            'price': 1
        }
        stock_dict2 = {
            'price': 2
        }
        offer_dict = {
            'name': 'foo',
            'stocks': [stock_dict1, stock_dict2],
            'type': 'bar'
        }
        offer = Offer(**offer_dict)

        # When
        ApiHandler.save(offer)

        # Then
        assert offer.name == offer_dict['name']
        assert set([s.price for s in offer.stocks]) == set([stock_dict1['price'], stock_dict2['price']])

    @with_delete
    def test_for_valid_relationship_dicts_with_nested_modifications(self, app):
        # Given
        offer_dict = {
            'name': 'foo',
            'type': 'bar'
        }
        offer = Offer(**offer_dict)
        ApiHandler.save(offer)
        stock_dict1 = {
            'offerId': humanize(offer.id),
            'price': 1
        }
        stock1 = Stock(**stock_dict1)
        ApiHandler.save(stock1)
        stock_dict1['id'] = humanize(stock1.id)
        stock_dict2 = {
            'offerId': humanize(offer.id),
            'price': 2
        }
        stock2 = Stock(**stock_dict2)
        ApiHandler.save(stock2)
        stock_dict2['id'] = humanize(stock2.id)
        stock_dict2['price'] = 3
        offer_dict['stocks'] = [stock_dict1, stock_dict2]
        offer.modify(offer_dict)

        # When
        ApiHandler.save(offer)

        # Then
        assert offer.name == offer_dict['name']
        offer_stock1 = [s for s in offer.stocks if s.id == stock1.id][0]
        offer_stock2 = [s for s in offer.stocks if s.id == stock2.id][0]
        assert offer_stock1.id == stock1.id
        assert offer_stock1.price == stock_dict1['price']
        assert offer_stock2.id == stock2.id
        assert offer_stock2.price == stock_dict2['price']
