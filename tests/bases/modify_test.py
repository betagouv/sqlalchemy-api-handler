import uuid
from datetime import datetime
from decimal import Decimal
import pytest
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.bases.errors import DateTimeCastError, \
                                                DecimalCastError, \
                                                EmptyFilterError, \
                                                ResourceNotFoundError, \
                                                UuidCastError
from sqlalchemy_api_handler.utils import dehumanize, \
                                         humanize, \
                                         NonDehumanizableId

from tests.conftest import with_delete
from api.models.foo import Foo
from api.models.offer import Offer
from api.models.offer_tag import OfferTag
from api.models.offerer import Offerer
from api.models.scope import ScopeType
from api.models.stock import Stock
from api.models.tag import Tag, TagType
from api.models.user import User
from api.models.user_offerer import UserOfferer
from api.models.time_interval import TimeInterval


time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)
now = datetime.utcnow()

class ModifyTest:
    def test_for_sql_integer_value_with_string_raises_decimal_cast_error(self):
        # Given
        test_object = Foo()
        data = {'integer_attribute': 'yolo'}

        # When
        with pytest.raises(DecimalCastError) as errors:
            test_object.modify(data)

        # Then
        assert errors.value.errors['integer_attribute'] == ["Invalid value for integer_attribute (integer): 'yolo'"]

    def test_for_sql_integer_value_with_str_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_object = Foo()
        data = {'integer_attribute': '12.9'}

        # When
        test_object.modify(data)

        # Then
        assert test_object.integer_attribute == Decimal('12.9')

    def test_for_sql_float_value_with_str_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_object = Foo()
        data = {'float_attribute': '12.9'}

        # When
        test_object.modify(data)

        # Then
        assert test_object.float_attribute == Decimal('12.9')

    def test_for_sql_integer_value_with_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_object = Foo()
        data = {'integer_attribute': 12}

        # When
        test_object.modify(data)

        # Then
        assert test_object.integer_attribute == 12

    def test_for_sql_float_value_with_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_object = Foo()
        data = {'float_attribute': 12.9}

        # When
        test_object.modify(data)

        # Then
        assert test_object.float_attribute == 12.9

    def test_for_valid_sql_uuid_value(self):
        # Given
        test_object = Foo()
        uuid_attribute = str(uuid.uuid4())
        data = {'uuid_attribute': uuid_attribute}

        # When
        test_object.modify(data)

        # Then
        assert test_object.uuid_attribute == uuid_attribute

    def test_for_valid_sql_uuid_value_with_key_finishing_by_Id(self):
        # Given
        test_object = Foo()
        uuid_id = str(uuid.uuid4())
        data = {'uuidId': uuid_id}

        # When
        test_object.modify(data)

        # Then
        assert test_object.uuidId == uuid_id

    def test_for_valid_sql_humanize_id_value_with_key_finishing_by_Id(self):
        # Given
        test_object = Foo()
        humanized_entity_id = "AE"
        data = {'entityId': humanized_entity_id}

        # When
        test_object.modify(data)

        # Then
        assert test_object.entityId == dehumanize(humanized_entity_id)


    def test_for_valid_sql_humanize_id_synonym_value_with_key_finishing_by_Id(self):
        # Given
        test_object = Foo()
        humanized_bar_id = "AE"
        dehumanized_bar_id = dehumanize(humanized_bar_id)
        data = {'barId': humanized_bar_id}

        # When
        test_object.modify(data)

        # Then
        assert test_object.bar_id == dehumanized_bar_id
        assert test_object.barId == dehumanized_bar_id


    def test_for_valid_relationship_dict(self):
        # Given
        test_object = Stock()
        offer_dict = { 'name': 'foo',
                       'type': 'bar' }
        stock_dict = { 'offer': offer_dict,
                       'price': 1 }

        # When
        test_object.modify(stock_dict)

        # Then
        assert test_object.price == stock_dict['price']
        assert test_object.offer.name == offer_dict['name']


    def test_for_valid_relationship_dicts(self):
        # Given
        test_object = Offer()
        stock_dict1 = { 'price': 1 }
        stock_dict2 = { 'price': 1 }
        offer_dict = {  'name': 'foo',
                        'stocks': [stock_dict1, stock_dict2],
                        'type': 'bar' }

        # When
        test_object.modify(offer_dict)

        # Then
        assert test_object.name == offer_dict['name']
        assert test_object.stocks[0].price == stock_dict1['price']
        assert test_object.stocks[1].price == stock_dict2['price']


    def test_for_sql_float_value_with_string_raises_decimal_cast_error(self):
        # Given
        test_object = Foo()
        data = {'float_attribute': 'yolo'}

        # When
        with pytest.raises(DecimalCastError) as errors:
            test_object.modify(data)

        # Then
        assert errors.value.errors['float_attribute'] == ["Invalid value for float_attribute (float): 'yolo'"]

    def test_for_sql_datetime_value_in_wrong_format_returns_400_and_affected_key_in_error(self):
        # Given
        test_object = Foo()
        data = {'date_attribute': {'date_attribute': None}}

        # When
        with pytest.raises(DateTimeCastError) as errors:
            test_object.modify(data)

        # Then
        assert errors.value.errors['date_attribute'] == [
            "Invalid value for date_attribute (datetime): {'date_attribute': None}"]

    def test_deserializes_datetimes(self):
        # Given
        raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': '2018-04-04T20:10:30.456Z'}

        # When
        time_interval.modify(raw_data)

        # Then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35, 123000)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30, 456000)

    def test_deserializes_datetimes_without_milliseconds(self):
        # Given
        raw_data = {'start': '2018-03-03T15:25:35', 'end': '2018-04-04T20:10:30'}

        # When
        time_interval.modify(raw_data)

        # Then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)

    def test_deserializes_datetimes_without_milliseconds_with_trailing_z(self):
        # Given
        raw_data = {'start': '2018-03-03T15:25:35Z', 'end': '2018-04-04T20:10:30Z'}

        # When
        time_interval.modify(raw_data)

        # Then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)

    def test_raises_type_error_if_raw_date_is_invalid(self):
        # Given
        raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': 'abcdef'}

        # When
        with pytest.raises(DateTimeCastError) as errors:
            time_interval.modify(raw_data)

        # Then
        assert errors.value.errors['end'] == ["Invalid value for end (datetime): 'abcdef'"]

    def test_raises_type_error_if_raw_uuid_is_invalid(self):
        # Given
        test_object = Foo()
        data = {'uuidId': 'foo'}

        # When
        with pytest.raises(UuidCastError) as errors:
            test_object.modify(data)

        # Then
        assert errors.value.errors['uuidId'] == [
            "Invalid value for uuidId (uuid): 'foo'"]

    def test_raises_type_error_if_raw_humanized_id_is_invalid(self):
        # Given
        test_object = Foo()
        data = {'entityId': '12R-..2foo'}

        # When
        with pytest.raises(NonDehumanizableId):
            test_object.modify(data)

    @with_delete
    def test_find_raise_empty_filter_error(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        with pytest.raises(EmptyFilterError) as errors:
            Offer.find({ '__SEARCH_BY__': 'position',
                         'name': 'fee',
                         'type': 'bric' })

        # Then
        assert errors.value.errors['_filter_from'] == ["None of filters found among: position"]

    @with_delete
    def test_find_returns_none(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.find({ '__SEARCH_BY__': 'name',
                              'name': 'fee',
                              'type': 'bric' })

        # Then
        assert offer2 is None

    @with_delete
    def test_find_returns_existing_offer(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.find({ '__SEARCH_BY__': 'name',
                              'name': 'foo' })

        # Then
        assert offer2.id == offer1.id
        assert offer2.name == offer1.name == 'foo'
        assert offer2.type == offer1.type == 'bar'

    @with_delete
    def test_find_or_create_returns_existing_offer(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.find_or_create({ '__SEARCH_BY__': 'name',
                                        'name': 'foo' })

        # Then
        assert offer2.id == offer1.id
        assert offer2.name == offer1.name == 'foo'
        assert offer2.type == offer1.type == 'bar'

    @with_delete
    def test_find_or_create_returns_created_offer(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.find_or_create({ '__SEARCH_BY__': 'name',
                                        'name': 'fee',
                                        'type': 'gold' })

        # Then
        assert offer2.id != offer1.id
        assert offer2.name == 'fee'
        assert offer2.type == 'gold'

    @with_delete
    def test_find_and_modify_returns_modified_offer(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.find_and_modify({ '__SEARCH_BY__': 'name',
                                         'name': 'foo',
                                         'type': 'bric' })

        # Then
        assert offer2.id == offer1.id
        assert offer2.name == offer1.name == 'foo'
        assert offer2.type == 'bric'

    @with_delete
    def test_find_and_modify_raises_ressource_not_found_error(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        with pytest.raises(ResourceNotFoundError) as e:
            Offer.find_and_modify({ '__SEARCH_BY__': 'name',
                                    'name': 'fee',
                                    'type': 'bric' })

        # Then
        assert e.value.errors['find_and_modify'] == ['No ressource found with {"name": "fee"} ']

    @with_delete
    def test_create_or_modify_returns_created_offer(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.create_or_modify({ '__SEARCH_BY__': 'name',
                                          'name': 'fee',
                                          'type': 'bric' })

        # Then
        assert offer2.id != offer1.id
        assert offer2.name == 'fee'
        assert offer2.type == 'bric'

    @with_delete
    def test_create_or_modify_returns_modified_offer(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.create_or_modify({ '__SEARCH_BY__': 'name',
                                          'name': 'foo',
                                          'type': 'bric' })

        # Then
        assert offer2.id == offer1.id
        assert offer2.name == offer1.name == 'foo'
        assert offer2.type == 'bric'


    @with_delete
    def test_create_or_modify_returns_modified_offerer_search_by_id(self, app):
        # Given
        offerer1 = Offerer(name="foo")
        ApiHandler.save(offerer1)

        # When
        offerer2 = Offerer.create_or_modify({ '__SEARCH_BY__': 'id',
                                              'id': humanize(offerer1.id),
                                              'name': 'fee' })

        # Then
        assert offerer2.id == offerer1.id
        assert offerer2.name == "fee"

    @with_delete
    def test_create_or_modify_returns_created_user_offerer_search_by_relationship_ids(self, app):
        # Given
        offerer = Offerer(name="foo")
        user = User(email="foo.marx@com", publicName="Foo Marx")
        ApiHandler.save(offerer, user)

        # When
        user_offerer = UserOfferer.create_or_modify({ '__SEARCH_BY__': ['offererId', 'userId'],
                                                      'rights': 'admin',
                                                      'offererId': humanize(offerer.id),
                                                      'userId': humanize(user.id) })

        # Then
        assert user_offerer.offererId == offerer.id
        assert user_offerer.rights == 'admin'
        assert user_offerer.userId == user.id


    @with_delete
    def test_create_or_modify_returns_modified_user_offerer_search_by_relationship_ids(self, app):
        # Given
        offerer = Offerer(name="foo")
        user = User(email="foo.marx@com", publicName="Foo Marx")
        user_offerer = UserOfferer(rights='admin',
                                   offerer=offerer,
                                   user=user)
        ApiHandler.save(user_offerer)

        # When
        user_offerer = UserOfferer.create_or_modify({ '__SEARCH_BY__': ['offererId', 'userId'],
                                                      'offererId': humanize(offerer.id),
                                                      'rights': 'editor',
                                                      'userId': humanize(user.id) })

        # Then
        assert user_offerer.offererId == offerer.id
        assert user_offerer.rights == 'editor'
        assert user_offerer.userId == user.id

    @with_delete
    def test_create_or_modify_returns_created_tag_with_nested_scope(self, app):
        # Given
        tag = Tag.create_or_modify({ '__SEARCH_BY__': 'label',
                                     'label': 'Very High',
                                     'scopes': [ { 'type': ScopeType.REVIEW } ] })

        # When
        ApiHandler.save(tag)

        # Then
        assert tag.scopes[0].tagId == tag.id

    @with_delete
    def test_create_or_modify_returns_modified_tag_with_nested_scope(self, app):
        # Given
        tag_dict = {
            '__SEARCH_BY__': 'label',
            'label': 'Very High',
            'scopes': [
                {
                    '__SEARCH_BY__': ['type'],
                    'type': ScopeType.REVIEW
                }
            ]
        }
        tag1 = Tag(**tag_dict)
        ApiHandler.save(tag1)

        # When
        tag2 = Tag.create_or_modify(tag_dict)
        ApiHandler.save(tag2)

        # Then
        assert tag2.id == tag1.id
        assert len(tag2.scopes) == 1
        assert tag2.scopes[0].tagId == tag2.id

    @with_delete
    def test_foo(self, app):
        # Given
        TAGS = [
            {
                'label': 'Accurate',
            },
            {
                'label': 'Biased',
            }
        ]
        for tag in TAGS:
            tag.update({
                '__SEARCH_BY__': ['label', 'type'],
                'id': '__NEXT_ID_IF_NOT_EXISTS__',
                'scopes': [{
                    '__SEARCH_BY__': ['tagId', 'type'],
                    'tagId': {
                        'humanized': True,
                        'key': 'id',
                        'type': '__PARENT__'
                    },
                    'type': ScopeType.REVIEW
                }],
                'type': TagType.QUALIFICATION
            })

        tags1 = []
        for tag_dict in TAGS:
            tag = Tag.create_or_modify(tag_dict)
            tags1.append(tag)
        ApiHandler.save(*tags1)

        # When
        tags2 = []
        for tag_dict in TAGS:
            tag = Tag.create_or_modify(tag_dict)
            tags2.append(tag)
        ApiHandler.save(*tags2)

        assert '/'.join([str(tag.id) for tag in tags1]) == '/'.join([str(tag.id) for tag in tags2])
        assert '/'.join([str(tag.scopes[0].id) for tag in tags1]) == '/'.join([str(tag.scopes[0].id) for tag in tags2])


    @with_delete
    def test_create_or_modify_with_relationship_search(self, app):
        # Given
        offer = Offer.create_or_modify({ '__SEARCH_BY__': 'name',
                                          'name': 'foo',
                                          'type': 'bar' },
                                        with_add=True,
                                        with_flush=True)
        stock1 = Stock.create_or_modify({ '__SEARCH_BY__': ['offer', 'price'],
                                          'offer': offer,
                                          'price': 2})

        # When
        stock2 = Stock.create_or_modify({ '__SEARCH_BY__': ['offer', 'price'],
                                          'offer': offer,
                                          'price': 3})

        #Then
        assert offer.id != None
        assert offer.name == 'foo'
        assert offer.type == 'bar'
        assert stock1.offer.id == offer.id
        assert stock2.offer.id == offer.id
        assert stock1.id == None
        assert stock2.id == None

    @with_delete
    def test_create_or_modify_with_relationships_search(self, app):
        # Given
        offer = Offer.create_or_modify({ '__SEARCH_BY__': 'name',
                                          'name': 'foo',
                                          'type': 'bar' },
                                        with_add=True,
                                        with_flush=True)
        tag = Tag.create_or_modify({ '__SEARCH_BY__': 'label',
                                     'label': 'car' },
                                     with_add=True,
                                     with_flush=True)

        # When
        offer_tag = OfferTag.create_or_modify({ '__SEARCH_BY__': ['offer', 'tag'],
                                                'offer': offer,
                                                'tag': tag })


        #Then
        assert offer.id != None
        assert offer.name == 'foo'
        assert offer.type == 'bar'
        assert tag.id != None
        assert tag.label == 'car'
        assert offer_tag.id == None

    @with_delete
    def test_modify_a_property_with_no_fset(self, app):
        # When
        stock = Stock()
        offer = Offer(name="foo", notDeletedStocks=[stock], type="bar")

        # Then
        assert offer.notDeletedStocks == []

    @with_delete
    def test_create_or_modify_with_primary_filter(self, app):
        # Given
        datum = {'name': 'foo', 'type': 'bar'}
        offer1 = Offer(**datum)
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.create_or_modify({'id': offer1.humanizedId, **datum})

        # Then
        assert offer2.id == offer1.id
        assert offer2.name == datum['name']

    @with_delete
    def test_create_or_modify_with_flatten_new_datum(self, app):
        # Given
        datum = {
                  'offer.name': 'foo',
                  'offer.offerTags.0.tag.label': 'bar',
                  'offer.type': 'bar',
                  'price': 2
                }

        # When
        stock = Stock.create_or_modify(datum)

        # Then
        for (key, value) in datum.items():
            assert stock.get(key) == value

        stock = Stock.create_or_modify(datum)
        for (key, value) in datum.items():
            assert stock.get(key) == value

    @with_delete
    def test_instance_from(self, app):
        # Given
        tag1 = Tag(label='foo')
        ApiHandler.save(tag1)

        # When
        tag2 = Tag.instance_from({ 'label': 'foo' })

        # Then
        assert tag1.id == tag2.id

    @with_delete
    def test_create_or_modify_with_flatten_search_existing_datum(self, app):
        # Given
        offer = Offer(name='foo', type='bar')
        ApiHandler.save(offer)
        datum = {
                  'offer.name': 'foo',
                  'offer.__SEARCH_BY__': 'name',
                  'offer.type': 'bar',
                  'price': 2,
                }

        # When
        stock = Stock.create_or_modify(datum)

        # Then
        for (key, value) in datum.items():
            if key.endswith('__SEARCH_BY__'):
                continue
            assert stock.get(key) == value
        assert stock.offer.id == offer.id

    @with_delete
    def test_create_or_modify_with_flatten_unique_existing_datum(self, app):
        # Given
        offer = Offer(name='foo', type='bar')
        ApiHandler.save(offer)
        datum = {
                  'offer.id': humanize(offer.id),
                  'offer.type': 'bar',
                  'price': 2,
                }

        # When
        stock = Stock.create_or_modify(datum)

        # Then
        for (key, value) in datum.items():
            if key.endswith('__SEARCH_BY__'):
                continue
            if key == 'offer.id':
                assert stock.get(key) == dehumanize(value)
            else:
                assert stock.get(key) == value
        assert stock.offer.id == offer.id

    @with_delete
    def test_create_or_modify_with_flatten_nested_unique_existing_datum(self, app):
        # Given
        tag = Tag(label='bar')
        ApiHandler.save(tag)
        datum = {
                  'name': 'foo',
                  'offerTags.0.tag.label': 'bar',
                  'type': 'bar',
                }

        # When
        offer = Offer.create_or_modify(datum)

        # Then
        for (key, value) in datum.items():
            if key.endswith('__SEARCH_BY__'):
                continue
            assert offer.get(key) == value
        assert offer.offerTags[0].tag.id == tag.id


    @with_delete
    def test_create_or_modify_retrieves_automatically_with_unique_datum(self, app):
        # Given
        tag1 = Tag(label='foo')
        ApiHandler.save(tag1)
        datum = {
                  'label': 'foo',
                }

        # When
        tag2 = Tag.create_or_modify(datum)

        # Then
        assert tag2.id == tag1.id
