import uuid
from datetime import datetime
from decimal import Decimal, \
                    InvalidOperation
from sqlalchemy import BigInteger, \
                       DateTime, \
                       Float, \
                       Integer, \
                       Numeric, \
                       String
from sqlalchemy.dialects.postgresql import UUID

from typing import List, Any, Iterable, Set

from sqlalchemy_api_handler.api_errors import DateTimeCastError, \
                                              DecimalCastError, \
                                              UuidCastError
from sqlalchemy_api_handler.bases.delete import Delete
from sqlalchemy_api_handler.bases.soft_delete import SoftDelete
from sqlalchemy_api_handler.utils.date import match_format
from sqlalchemy_api_handler.utils.human_ids import dehumanize, is_id_column


class Populate(
        Delete,
        SoftDelete
):
    def __init__(self, **options):
        self.populate_from_dict(options)

    def populate_from_dict(self, datum: dict, skipped_keys: List[str] = []):
        self.check_not_soft_deleted()
        columns = self.__mapper__.columns
        columns_keys_to_populate = self._get_column_keys_to_populate(
            set(columns.keys()), datum, skipped_keys)
        for key in columns_keys_to_populate:
            column = columns[key]
            value = _dehumanize_if_needed(column, datum.get(key))
            if isinstance(value, str):
                if isinstance(column.type, Integer):
                    self._try_to_set_attribute_with_decimal_value(column, key, value, 'integer')
                elif isinstance(column.type, (Float, Numeric)):
                    self._try_to_set_attribute_with_decimal_value(column, key, value, 'float')
                elif isinstance(column.type, String):
                    setattr(self, key, value.strip() if value else value)
                elif isinstance(column.type, DateTime):
                    self._try_to_set_attribute_with_deserialized_datetime(column, key, value)
                elif isinstance(column.type, UUID):
                    self._try_to_set_attribute_with_uuid(column, key, value)
            elif not isinstance(value, datetime) and isinstance(column.type, DateTime):
                self._try_to_set_attribute_with_deserialized_datetime(column, key, value)
            else:
                setattr(self, key, value)

        for (key, relationship) in self.__mapper__.relationships.items():
            if key in datum:
                model = relationship.mapper.class_
                value = self._get_model_instance(datum[key], model)
                if value:
                    setattr(self, key, value)

        for (key, synonym) in self.__mapper__.synonyms.items():
            if key in datum:
                value = _dehumanize_if_needed(
                    synonym._proxied_property.columns[0],
                    datum[key]
                )
                setattr(self, key, value)


    @staticmethod
    def _get_column_keys_to_populate(column_keys: Set[str], data: dict, skipped_keys: Iterable[str]) -> Set[str]:
        requested_columns_to_update = set(data.keys())
        forbidden_columns = set(['id', 'deleted'] + skipped_keys)
        allowed_columns_to_update = requested_columns_to_update - forbidden_columns
        keys_to_populate = column_keys.intersection(allowed_columns_to_update)
        return keys_to_populate

    @staticmethod
    def _get_model_instance(value, model):
        if not isinstance(value, model):
            if hasattr(value, 'items'):
                primary_key_columns = model.__mapper__.primary_key
                primary_keys = [column.key for column in primary_key_columns]
                primary_keys_values = list(map(lambda primary_key: value.get(primary_key), primary_keys))
                if all(primary_keys_values):
                    pks = [
                        _dehumanize_if_needed(column, primary_keys_values[index])
                        for (index, column) in enumerate(primary_key_columns)
                    ]
                    model_instance = model.query.get(pks)
                    model_instance.populate_from_dict(value)
                    return model_instance
                return model(**value)
            elif hasattr(value, '__iter__'):
                return list(map(lambda obj: Populate._get_model_instance(obj, model), value))
        return value

    def _try_to_set_attribute_with_deserialized_datetime(self, col, key, value):
        try:
            datetime_value = _deserialize_datetime(key, value)
            setattr(self, key, datetime_value)
        except TypeError:
            error = DateTimeCastError()
            error.add_error(col.name, "Invalid value for %s (datetime): %r" % (key, value))
            raise error

    def _try_to_set_attribute_with_uuid(self, col, key, value):
        try:
            uuid_obj = uuid.UUID(value)
            setattr(self, key, value)
        except ValueError:
            error = UuidCastError()
            error.add_error(col.name, "Invalid value for %s (uuid): %r" % (key, value))
            raise error

    def _try_to_set_attribute_with_decimal_value(self, col, key, value, expected_format):
        try:
            setattr(self, key, Decimal(value))
        except InvalidOperation:
            error = DecimalCastError()
            error.add_error(col.name, "Invalid value for {} ({}): '{}'".format(key, expected_format, value))
            raise error


    @classmethod
    def create_or_modify(model, content, search_by):
        if not isinstance(search_by, list):
            search_by = [search_by]

        filter = dict([(search_key, content[search_key])  for search_key in search_by])

        existing_object = model.query.filter_by(**filter).first()
        if existing_object:
            existing_object.populate_from_dict(content)
            return existing_object

        return model(**content)


def _dehumanize_if_needed(column, value: Any) -> Any:
    if is_id_column(column):
        return dehumanize(value)
    return value


def _deserialize_datetime(key, value):
    if value is None:
        return None

    valid_patterns = ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']
    datetime_value = None

    for pattern in valid_patterns:
        if match_format(value, pattern):
            datetime_value = datetime.strptime(value, pattern)

    if not datetime_value:
        raise TypeError('Invalid value for %s: %r' % (key, value), 'datetime', key)

    return datetime_value
