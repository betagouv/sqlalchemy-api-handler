import json
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
                                              UuidCastError, \
                                              ResourceNotFoundError, \
                                              EmptyFiltersError

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
    def _get_filter_dict(model, content, filter_keys):
        if not isinstance(filter_keys, list):
            filter_keys = [filter_keys]
        return dict([(key, value) for key, value in content.items() if key in filter_keys])

    @classmethod
    def _update(model, object, content):
        object.populate_from_dict(content)
        return object

    @classmethod
    def _create(model, content):
        return model(**content)

    @classmethod
    def find(model, content, filter_keys):
        filters = model._get_filter_dict(content, filter_keys)
        if not filters:
            errors = EmptyFiltersError()
            filters = ", ".join(filter_keys) if isinstance(filter_keys, list) else filter_keys
            errors.add_error('_get_filter_dict', 'None of filters found among: ' + filters)
            raise errors
        existing = model.query.filter_by(**filters).first()
        if not existing:
            return None
        return existing

    @classmethod
    def find_or_create(model, content, filter_keys):
        existing = model.find(content, filter_keys)
        if existing:
            return existing
        return model._create(content)

    @classmethod
    def find_and_update(model, content, filter_keys):
        existing = model.find(content, filter_keys)
        if not existing:
            errors = ResourceNotFoundError()
            filters = model._get_filter_dict(content, filter_keys)
            errors.add_error('find_and_update', 'No ressource found with {} '.format(json.dumps(filters)))
            raise errors
        return model._update(existing, content)

    @classmethod
    def create_or_update(model, content, filter_keys):
        existing = model.find(content, filter_keys)
        if existing:
            return model._update(existing, content)
        return model._create(content)


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
