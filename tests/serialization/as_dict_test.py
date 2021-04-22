from concurrent.futures import ThreadPoolExecutor

from api.models.offer import Offer
from api.models.offer_tag import OfferTag
from api.models.stock import Stock
from api.models.tag import Tag
from api.models.user import User
from sqlalchemy_api_handler.serialization import as_dict


class AsDictTest:
    def test_simple_dictify(self, app):
        # given
        user_fields_dict = {
            'email': 'marx.foo@plop.fr',
            'firstName': 'Marx',
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
            'firstName': 'Marx',
            'lastName': 'Foo',
            'publicName': 'Marx Foo'
        }
        user = User(**user_fields_dict)

        # when
        user_dict = as_dict(user, includes=['-email'])

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
            'firstName': 'Marx',
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
            'firstName': 'Marx',
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

    def test_dictify_with_sync_map(self, app):
        # given
        offer = Offer(name='foo', type='bar')
        tag1 = Tag(label='beep')
        offer_tag1 = OfferTag(offer=offer, tag=tag1)
        tag2 = Tag(label='boop')
        offer_tag2 = OfferTag(offer=offer, tag=tag2)

        # when
        includes = [{'key': 'offerTags', 'includes': ['tag']}]
        offer_dict = as_dict(offer,
                             includes=includes)

        # then
        assert len(offer_dict['offerTags']) == 2
        assert offer_dict['offerTags'][0]['tag']['label'] == 'beep'
        assert offer_dict['offerTags'][1]['tag']['label'] == 'boop'

    def test_dictify_with_async_map_key(self, app):
        # given
        offer_tags_count = 10
        offer = Offer(name='foo', type='bar')
        offer_tags = []
        for index in range(0, offer_tags_count):
            tag = Tag(label=str(index))
            offer_tags.append(OfferTag(offer=offer, tag=tag))

        # when
        includes = ['|offerTags']
        offer_dict = as_dict(offer,
                             includes=includes)

        # then
        assert len(offer_dict['offerTags']) == offer_tags_count
        for index in range(0, offer_tags_count):
            assert offer_dict['offerTags'][index]['tagId'] == offer_tags[index].id

    def test_dictify_with_async_map_join(self, app):
        # given
        offer_tags_count = 10
        offer = Offer(name='foo', type='bar')
        offer_tags = []
        for index in range(0, offer_tags_count):
            tag = Tag(label=str(index))
            offer_tags.append(OfferTag(offer=offer, tag=tag))

        # when
        includes = [{'key': '|offerTags', 'includes': ['tag']}]
        offer_dict = as_dict(offer,
                             includes=includes)

        # then
        assert len(offer_dict['offerTags']) == offer_tags_count
        for index in range(0, offer_tags_count):
            assert offer_dict['offerTags'][index]['tag']['label'] == str(index)
            assert offer_dict['offerTags'][index]['tag']['sleptFoo'] == 0

    def test_dictify_with_custom_async_map_join(self, app):
        # given
        offer_tags_count = 10
        offer = Offer(name='foo', type='bar')
        offer_tags = []
        for index in range(0, offer_tags_count):
            tag = Tag(label=str(index))
            offer_tags.append(OfferTag(offer=offer, tag=tag))

        # when
        includes = [{'key': '|offerTags', 'includes': ['tag']}]
        with ThreadPoolExecutor(max_workers=5) as executor:
            offer_dict = as_dict(offer,
                                 async_map=executor.map,
                                 includes=includes)

            # then
            assert len(offer_dict['offerTags']) == offer_tags_count
            for index in range(0, offer_tags_count):
                assert offer_dict['offerTags'][index]['tag']['label'] == str(index)
                assert offer_dict['offerTags'][index]['tag']['sleptFoo'] == 0

    def test_should_return_soft_deleted_entities_when_option_is_given(self):
        # given
        offer = Offer(name='foo', type='bar')
        stock1 = Stock(price=10, isSoftDeleted=True)
        stock2 = Stock(price=5, isSoftDeleted=False)
        offer.stocks = [stock1, stock2]
        includes = [{'key': 'stocks', 'includes': ['price'], 'with_soft_deleted_entities': True}]

        # when
        offer_dict = as_dict(offer, includes=includes)

        # then
        assert len(offer_dict['stocks']) == 2
