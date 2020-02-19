import pytest
from sqlalchemy_api_handler.serialization.as_dict import as_dict
from tests.test_utils.models.offer import Offer
from tests.test_utils.models.stock import Stock
from tests.test_utils.models.user import User

class AsDictTest:
    def test_simple_dictify(self, app):
        # given
        user_fields_dict = {
            "email": "marx.foo@plop.fr",
            "firstName" : "Marx",
            "lastName": "Foo",
            "publicName": "Marx Foo"
        }
        user = User(**user_fields_dict)

        # when
        user_dict = as_dict(user)

        # then
        assert set(user_fields_dict).issubset(user_dict)

    def test_dictify_with_removing_includes(self, app):
        # given
        user_fields_dict = {
            "email": "marx.foo@plop.fr",
            "firstName" : "Marx",
            "lastName": "Foo",
            "publicName": "Marx Foo"
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
            "email": "marx.foo@plop.fr",
            "firstName" : "Marx",
            "lastName": "Foo",
            "metier": "philosophe",
            "publicName": "Marx Foo"
        }
        user = User(**user_fields_dict)

        # when
        user_dict = as_dict(user)

        # then
        assert 'metier' not in user_dict
        assert user_dict['job'] == user_fields_dict['metier']
