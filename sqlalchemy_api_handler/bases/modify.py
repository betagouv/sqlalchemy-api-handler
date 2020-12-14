# pylint: disable=W0212

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
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Sequence
from typing import List, Any, Iterable, Set

from sqlalchemy_api_handler.bases.delete import Delete
from sqlalchemy_api_handler.bases.errors import DateTimeCastError, \
                                                DecimalCastError, \
                                                EmptyFilterError, \
                                                ResourceNotFoundError, \
                                                UuidCastError
from sqlalchemy_api_handler.bases.soft_delete import SoftDelete
from sqlalchemy_api_handler.utils.date import match_format
from sqlalchemy_api_handler.utils.dehumanize import dehumanize
from sqlalchemy_api_handler.utils.humanize import humanize
from sqlalchemy_api_handler.utils.is_id_column import is_id_column


class Modify(Delete, SoftDelete):
    def __init__(self, **initial_datum):
        self.modify(initial_datum)

    def modify(self,
               datum: dict,
               skipped_keys: List[str] = [],
               with_add=False,
               with_check_not_soft_deleted=True):

        if with_add:
            Modify.add(self)

        if with_check_not_soft_deleted:
            self.check_not_soft_deleted()

        datum_keys_with_skipped_keys = set(datum.keys()) - set(skipped_keys)

        columns = self.__mapper__.columns
        column_keys_to_modify = set(columns.keys()).intersection(datum_keys_with_skipped_keys)
        for key in column_keys_to_modify:
            column = columns[key]
            value = dehumanize_if_needed(column, datum.get(key))
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

        relationships = self.__mapper__.relationships
        relationship_keys_to_modify = set(relationships.keys()).intersection(datum_keys_with_skipped_keys)
        for key in relationship_keys_to_modify:
            relationship = relationships[key]
            model = relationship.mapper.class_
            value = model.instance_from(datum[key], parent=self)
            if value:
                setattr(self, key, value)

        synonyms = self.__mapper__.synonyms
        synonym_keys_to_modify = set(synonyms.keys()).intersection(datum_keys_with_skipped_keys)
        for key in synonym_keys_to_modify:
            value = dehumanize_if_needed(synonyms[key]._proxied_property.columns[0],
                                         datum[key])
            setattr(self, key, value)

        other_keys_to_modify = datum_keys_with_skipped_keys \
                                - column_keys_to_modify \
                                - relationship_keys_to_modify \
                                - synonym_keys_to_modify
        for key in other_keys_to_modify:
            if hasattr(self.__class__, key):
                value_type = getattr(self.__class__, key)
                if isinstance(value_type, property) and value_type.fset is None:
                    return
            setattr(self, key, datum[key])

        return self

    @classmethod
    def instance_from_primary_value(model, value):
        primary_key_columns = model.__mapper__.primary_key
        primary_keys = [
            column.key
            for column in primary_key_columns
        ]
        primary_keys_values = [
            value.get(primary_key)
            for primary_key in primary_keys
        ]
        if all(primary_keys_values):
            pks = [
                dehumanize_if_needed(column, primary_keys_values[index])
                for (index, column) in enumerate(primary_key_columns)
            ]
            instance = model.query.get(pks)
            return instance.modify(value)

    @classmethod
    def instance_from_search_by_value(model, value, parent=None):
        value_dict = {}
        for (column_name, sub_value) in value.items():
            column_value = sub_value
            if hasattr(sub_value, 'items') \
                and 'type' in sub_value \
                and sub_value['type'] == '__PARENT__':
                column_value = getattr(parent, sub_value['key'])
                if 'humanized' in sub_value and sub_value['humanized']:
                    column_value = humanize(column_value)
            value_dict[column_name] = column_value
        return model.create_or_modify(value_dict)

    @classmethod
    def instance_from(model,
                      value,
                      parent=None):
        if not isinstance(value, model):
            if hasattr(value, 'items'):
                instance = model.instance_from_primary_value(value)
                if instance:
                    return instance
                if '__SEARCH_BY__' in value:
                    return model.instance_from_search_by_value(value,
                                                               parent=parent)
                return model(**value)

            if hasattr(value, '__iter__'):
                return [
                    model.instance_from(obj, parent=parent)
                    for obj in value
                ]
        return value

    def _try_to_set_attribute_with_deserialized_datetime(self, col, key, value):
        try:
            datetime_value = _deserialize_datetime(key, value)
            setattr(self, key, datetime_value)
        except TypeError:
            error = DateTimeCastError()
            error.add_error(col.name, 'Invalid value for %s (datetime): %r' % (key, value))
            raise error

    def _try_to_set_attribute_with_uuid(self, col, key, value):
        try:
            uuid_obj = uuid.UUID(value)
            setattr(self, key, value)
        except ValueError:
            error = UuidCastError()
            error.add_error(col.name, 'Invalid value for %s (uuid): %r' % (key, value))
            raise error

    def _try_to_set_attribute_with_decimal_value(self, col, key, value, expected_format):
        try:
            setattr(self, key, Decimal(value))
        except InvalidOperation:
            error = DecimalCastError()
            error.add_error(col.name, "Invalid value for {} ({}): '{}'".format(key, expected_format, value))
            raise error

    @classmethod
    def _filter_from(model, datum):
        if '__SEARCH_BY__' not in datum or not datum['__SEARCH_BY__']:
            errors = EmptyFilterError()
            errors.add_error('_filter_from', 'No __SEARCH_BY__ item inside datum')
            raise errors

        search_by_keys = datum['__SEARCH_BY__']
        if not isinstance(search_by_keys, list):
            search_by_keys = [search_by_keys]
        search_by_keys = set(search_by_keys)

        filter_dict = {}

        columns = model.__mapper__.columns
        column_keys = set(columns.keys()).intersection(search_by_keys)
        for key in column_keys:
            column = columns[key]
            value = dehumanize_if_needed(column, datum.get(key))
            filter_dict[key] = value

        relationships = model.__mapper__.relationships
        relationship_keys = set(relationships.keys()).intersection(search_by_keys)
        for key in relationship_keys:
            if key in search_by_keys:
                filter_dict[key] = datum.get(key)

        synonyms = model.__mapper__.synonyms
        synonym_keys = set(synonyms.keys()).intersection(search_by_keys)
        for key in synonym_keys:
            column = synonyms[key]._proxied_property.columns[0]
            if key in search_by_keys:
                value = dehumanize_if_needed(column, datum.get(key))
                filter_dict[key] = value

        return filter_dict

    @classmethod
    def _created_from(model, datum):
        created = {**datum}
        if 'id' in created and created['id'] == '__NEXT_ID_IF_NOT_EXISTS__':
            db = Modify.get_db()
            seq = Sequence('{}_id_seq'.format(model.__tablename__))
            created['id'] = humanize(db.session.execute(seq))
        return created

    @classmethod
    def _existing_from(model, datum):
        existing = {**datum}
        if 'id' in existing and existing['id'] == '__NEXT_ID_IF_NOT_EXISTS__':
            del existing['id']
        return existing

    @classmethod
    def find(model, datum):
        filters = model._filter_from(datum)
        if not filters:
            search_by = datum['__SEARCH_BY__']
            errors = EmptyFilterError()
            filters = ', '.join(search_by) if isinstance(search_by, list) else search_by
            errors.add_error('_filter_from', 'None of filters found among: ' + filters)
            raise errors
        entity = model.query.filter_by(**filters).first()
        if not entity:
            return None
        return entity

    @classmethod
    def find_or_create(model, datum):
        entity = model.find(datum)
        if entity:
            return entity
        return model(**model._created_from(datum))

    @classmethod
    def find_and_modify(model, datum):
        entity = model.find(datum)
        if not entity:
            errors = ResourceNotFoundError()
            filters = model._filter_from(datum)
            errors.add_error('find_and_modify', 'No ressource found with {} '.format(json.dumps(filters)))
            raise errors
        return model.modify(entity, model._existing_from(datum))

    @classmethod
    def create_or_modify(model, datum):
        entity = model.find(datum)
        if entity:
            return model.modify(entity, model._existing_from(datum))
        return model(**model._created_from(datum))

def dehumanize_if_needed(column, value: Any) -> Any:
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
