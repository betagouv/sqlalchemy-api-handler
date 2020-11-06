import pytest
from sqlalchemy_api_handler.serialization import as_dict
from api.models.offer import Offer
from api.models.stock import Stock
from api.models.user import User

class AsDictTest:
    def test_simple_dictify(self, app):
        # given
        user_fields_dict = {
            'email': 'marx.foo@plop.fr',
            'firstName' : 'Marx',
            'lastName': 'Foo',
            'publicName': 'Marx Foo'
        }
        user = User(**user_fields_dict)

        # when
        user_dict = as_dict(user)

        # then
        assert set(user_fields_dict).issubset(user_dict)

    def test_dictify_with_removing_includes(self, app):
        # given
        user_fields_dict = {
            'email': 'marx.foo@plop.fr',
            'firstName' : 'Marx',
            'lastName': 'Foo',
            'publicName': 'Marx Foo'
        }
        user = User(**user_fields_dict)

        # when
        user_dict = as_dict(user, includes=["-email"])

        # then
        user_fields_dict_without_email = dict(user_fields_dict)
        del user_fields_dict_without_email['email']
        assert set(user_fields_dict_without_email).issubset(user_dict)
        assert 'email' not in user_dict

    def test_dictify_with_relationships_includes(self, app):
        # given
        offer = Offer()
        stock = Stock()
        offer.stocks = [stock]

        # when
        stock_dict = as_dict(stock)
        offer_dict = as_dict(offer, includes=["stocks"])

        # then
        assert 'stocks' in offer_dict
        assert len(offer_dict['stocks']) == 1
        assert offer_dict['stocks'][0]['id'] == stock_dict['id']

    def test_dictify_with_default_class_includes(self, app):
        # given
        user_fields_dict = {
            'email': 'marx.foo@plop.fr',
            'firstName' : 'Marx',
            'lastName': 'Foo',
            'metier': 'philosophe',
            'publicName': 'Marx Foo'
        }
        user = User(**user_fields_dict)

        # when
        user_dict = as_dict(user)

        # then
        assert 'metier' not in user_dict
        assert user_dict['job'] == user_fields_dict['metier']

    def test_dictify_with_only_includes(self, app):
        # given
        user_fields_dict = {
            'email': 'marx.foo@plop.fr',
            'firstName' : 'Marx',
            'lastName': 'Foo',
            'metier': 'philosophe',
            'publicName': 'Marx Foo'
        }
        user = User(**user_fields_dict)

        # when
        includes = ['email', 'metier']
        user_dict = as_dict(user,
                            includes=includes,
                            mode='only-includes')

        # then
        assert len(user_dict) == len(includes)
        assert set(user_dict.keys()) == set(includes)
        assert set(user_dict.values()) == set(map(lambda key: user_fields_dict[key], includes))
