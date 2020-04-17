import uuid
from datetime import datetime
from decimal import Decimal
import pytest
from sqlalchemy import BigInteger, Column, DateTime, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, synonym
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.api_errors import DateTimeCastError, \
                                              DecimalCastError, \
                                              UuidCastError
from sqlalchemy_api_handler.utils.human_ids import dehumanize, NonDehumanizableId

from tests.conftest import clean_database
from tests.test_utils.db import Model
from tests.test_utils.models.offer import Offer
from tests.test_utils.models.stock import Stock
from tests.test_utils.models.user import User
from tests.test_utils.models.time_interval import TimeInterval


class PopulateFoo(ApiHandler, Model):
    date_attribute = Column(DateTime(), nullable=True)
    entityId = Column(BigInteger(), nullable=True)
    float_attribute = Column(Float(), nullable=True)
    integer_attribute = Column(Integer(), nullable=True)
    uuid_attribute = Column(UUID(as_uuid=True), nullable=True)
    uuidId = Column(UUID(as_uuid=True), nullable=True)
    bar_id = Column(BigInteger())
    barId = synonym('bar_id')

time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)
now = datetime.utcnow()

class PopulateTest:
    def test_user_string_fields_are_stripped_of_whitespace(self):
        # Given
        user_data = {
            'email': '   test@example.com',
            'firstName': 'John   ',
            'lastName': None,
            'postalCode': '   93100   ',
            'publicName': ''
        }

        # When
        user = User(**user_data)

        # Then
        assert user.email == 'test@example.com'
        assert user.firstName == 'John'
        assert user.lastName == None
        assert user.postalCode == '93100'
        assert user.publicName == ''

    def test_for_sql_integer_value_with_string_raises_decimal_cast_error(self):
        # Given
        test_object = PopulateFoo()
        data = {'integer_attribute': 'yolo'}

        # When
        with pytest.raises(DecimalCastError) as errors:
            test_object.populate_from_dict(data)

        # Then
        assert errors.value.errors['integer_attribute'] == ["Invalid value for integer_attribute (integer): 'yolo'"]

    def test_for_sql_integer_value_with_str_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_object = PopulateFoo()
        data = {'integer_attribute': '12.9'}

        # When
        test_object.populate_from_dict(data)

        # Then
        assert test_object.integer_attribute == Decimal('12.9')

    def test_for_sql_float_value_with_str_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_object = PopulateFoo()
        data = {'float_attribute': '12.9'}

        # When
        test_object.populate_from_dict(data)

        # Then
        assert test_object.float_attribute == Decimal('12.9')

    def test_for_sql_integer_value_with_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_object = PopulateFoo()
        data = {'integer_attribute': 12}

        # When
        test_object.populate_from_dict(data)

        # Then
        assert test_object.integer_attribute == 12

    def test_for_sql_float_value_with_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_object = PopulateFoo()
        data = {'float_attribute': 12.9}

        # When
        test_object.populate_from_dict(data)

        # Then
        assert test_object.float_attribute == 12.9

    def test_for_valid_sql_uuid_value(self):
        # Given
        test_object = PopulateFoo()
        uuid_attribute = str(uuid.uuid4())
        data = {'uuid_attribute': uuid_attribute}

        # When
        test_object.populate_from_dict(data)

        # Then
        assert test_object.uuid_attribute == uuid_attribute

    def test_for_valid_sql_uuid_value_with_key_finishing_by_Id(self):
        # Given
        test_object = PopulateFoo()
        uuid_id = str(uuid.uuid4())
        data = {'uuidId': uuid_id}

        # When
        test_object.populate_from_dict(data)

        # Then
        assert test_object.uuidId == uuid_id

    def test_for_valid_sql_humanize_id_value_with_key_finishing_by_Id(self):
        # Given
        test_object = PopulateFoo()
        humanized_entity_id = "AE"
        data = {'entityId': humanized_entity_id}

        # When
        test_object.populate_from_dict(data)

        # Then
        assert test_object.entityId == dehumanize(humanized_entity_id)


    def test_for_valid_sql_humanize_id_synonym_value_with_key_finishing_by_Id(self):
        # Given
        test_object = PopulateFoo()
        humanized_bar_id = "AE"
        dehumanized_bar_id = dehumanize(humanized_bar_id)
        data = {'barId': humanized_bar_id}

        # When
        test_object.populate_from_dict(data)

        # Then
        assert test_object.bar_id == dehumanized_bar_id
        assert test_object.barId == dehumanized_bar_id


    def test_for_valid_relationship_dict(self):
        # Given
        test_object = Stock()
        offer_dict = {
            "name": "foo",
            "type": "bar"
        }
        stock_dict = {
            "offer": offer_dict,
            "price": 1
        }

        # When
        test_object.populate_from_dict(stock_dict)

        # Then
        assert test_object.price == stock_dict['price']
        assert test_object.offer.name == offer_dict['name']


    def test_for_valid_relationship_dicts(self):
        # Given
        test_object = Offer()
        stock_dict1 = {
            "price": 1
        }
        stock_dict2 = {
            "price": 1
        }
        offer_dict = {
            "name": "foo",
            "stocks": [stock_dict1, stock_dict2],
            "type": "bar"
        }

        # When
        test_object.populate_from_dict(offer_dict)

        # Then
        assert test_object.name == offer_dict['name']
        assert test_object.stocks[0].price == stock_dict1['price']
        assert test_object.stocks[1].price == stock_dict2['price']


    def test_for_sql_float_value_with_string_raises_decimal_cast_error(self):
        # Given
        test_object = PopulateFoo()
        data = {'float_attribute': 'yolo'}

        # When
        with pytest.raises(DecimalCastError) as errors:
            test_object.populate_from_dict(data)

        # Then
        assert errors.value.errors['float_attribute'] == ["Invalid value for float_attribute (float): 'yolo'"]

    def test_for_sql_datetime_value_in_wrong_format_returns_400_and_affected_key_in_error(self):
        # Given
        test_object = PopulateFoo()
        data = {'date_attribute': {'date_attribute': None}}

        # When
        with pytest.raises(DateTimeCastError) as errors:
            test_object.populate_from_dict(data)

        # Then
        assert errors.value.errors['date_attribute'] == [
            "Invalid value for date_attribute (datetime): {'date_attribute': None}"]

    def test_deserializes_datetimes(self):
        # Given
        raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': '2018-04-04T20:10:30.456Z'}

        # When
        time_interval.populate_from_dict(raw_data)

        # Then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35, 123000)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30, 456000)

    def test_deserializes_datetimes_without_milliseconds(self):
        # Given
        raw_data = {'start': '2018-03-03T15:25:35', 'end': '2018-04-04T20:10:30'}

        # When
        time_interval.populate_from_dict(raw_data)

        # Then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)

    def test_deserializes_datetimes_without_milliseconds_with_trailing_z(self):
        # Given
        raw_data = {'start': '2018-03-03T15:25:35Z', 'end': '2018-04-04T20:10:30Z'}

        # When
        time_interval.populate_from_dict(raw_data)

        # Then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)

    def test_raises_type_error_if_raw_date_is_invalid(self):
        # Given
        raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': 'abcdef'}

        # When
        with pytest.raises(DateTimeCastError) as errors:
            time_interval.populate_from_dict(raw_data)

        # Then
        assert errors.value.errors['end'] == ["Invalid value for end (datetime): 'abcdef'"]

    def test_raises_type_error_if_raw_uuid_is_invalid(self):
        # Given
        test_object = PopulateFoo()
        data = {'uuidId': 'foo'}

        # When
        with pytest.raises(UuidCastError) as errors:
            test_object.populate_from_dict(data)

        # Then
        assert errors.value.errors['uuidId'] == [
            "Invalid value for uuidId (uuid): 'foo'"]

    def test_raises_type_error_if_raw_humanized_id_is_invalid(self):
        # Given
        test_object = PopulateFoo()
        data = {'entityId': '12R-..2foo'}

        # When
        with pytest.raises(NonDehumanizableId):
            test_object.populate_from_dict(data)


    @clean_database
    def test_create_or_update_returns_new_created_offer(self, app):
        # Given
        offer1 = Offer(name='foo', type='bar')
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.create_or_modify(
            { 'name': 'fee', 'type': 'bric' },
            search_by='name'
        )

        # Then
        assert offer2.id != offer1.id
        assert offer2.name == 'fee'
        assert offer2.type == 'bric'


    @clean_database
    def test_create_or_update_returns_modified_existing_offer(self, app):
        # Given
        offer1 = Offer(name="foo", type="bar")
        ApiHandler.save(offer1)

        # When
        offer2 = Offer.create_or_modify(
            { 'name': 'foo', 'type': 'bric' },
            search_by='name'
        )

        # Then
        assert offer2.id == offer1.id
        assert offer2.name == 'foo'
        assert offer2.type == 'bric'
