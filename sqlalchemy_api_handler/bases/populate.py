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
from sqlalchemy.sql.schema import Column
from typing import List, Any, Iterable, Set

from sqlalchemy_api_handler.api_errors import DateTimeCastError, \
                                              DecimalCastError, \
                                              UuidCastError
from sqlalchemy_api_handler.bases.delete import Delete
from sqlalchemy_api_handler.bases.soft_delete import SoftDelete
from sqlalchemy_api_handler.utils.date import match_format
from sqlalchemy_api_handler.utils.human_ids import dehumanize


class Populate(
        Delete,
        SoftDelete
):
    def __init__(self, **options):
        self.populate_from_dict(options)

    def populate_from_dict(self, datum: dict, skipped_keys: List[str] = []):
        self.check_not_soft_deleted()
        columns = self.__class__.__table__.columns._data
        keys_to_populate = self._get_keys_to_populate(columns, datum, skipped_keys)
        for key in keys_to_populate:
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

    @staticmethod
    def _get_keys_to_populate(columns: Iterable[str], data: dict, skipped_keys: Iterable[str]) -> Set[str]:
        requested_columns_to_update = set(data.keys())
        forbidden_columns = set(['id', 'deleted'] + skipped_keys)
        allowed_columns_to_update = requested_columns_to_update - forbidden_columns
        keys_to_populate = set(columns).intersection(allowed_columns_to_update)
        return keys_to_populate

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

def _dehumanize_if_needed(column, value: Any) -> Any:
    if _is_human_id_column(column):
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

def _is_human_id_column(column: Column) -> bool:
    if column is not None:
        return (column.key == 'id' or column.key.endswith('Id')) and isinstance(column.type, (BigInteger, Integer))
