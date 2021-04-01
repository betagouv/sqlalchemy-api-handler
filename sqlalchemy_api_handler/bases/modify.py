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
from typing import List, Iterable, Set

from sqlalchemy_api_handler.bases.delete import Delete
from sqlalchemy_api_handler.bases.errors import DateTimeCastError, \
                                                DecimalCastError, \
                                                EmptyFilterError, \
                                                ResourceNotFoundError, \
                                                UuidCastError
from sqlalchemy_api_handler.bases.soft_delete import SoftDelete
import sqlalchemy_api_handler.utils.date as date_helper
from sqlalchemy_api_handler.utils.datum import nesting_datum_from
from sqlalchemy_api_handler.utils.dehumanize import dehumanize, \
                                                    dehumanize_if_needed
from sqlalchemy_api_handler.utils.humanize import humanize
from sqlalchemy_api_handler.utils.is_id_column import is_id_column


class Modify(Delete, SoftDelete):
    def __init__(self, **initial_datum):
        self.modify(initial_datum)

    def modify(self,
               datum: dict,
               skipped_keys: List[str] = [],
               with_add=False,
               with_check_not_soft_deleted=True,
               with_flush=False,
               with_no_autoflush=True):

        if with_add:
            Modify.add(self)

        if with_check_not_soft_deleted:
            self.check_not_soft_deleted()

        datum_keys_with_skipped_keys = set(datum.keys()) - set(skipped_keys)

        columns = self.__mapper__.columns
        column_keys_to_modify = set(columns.keys()).intersection(datum_keys_with_skipped_keys)
        for key in column_keys_to_modify:
            column = columns[key]
            self._try_to_set_attribute(column, key, datum.get(key))

        relationships = self.__mapper__.relationships
        relationship_keys_to_modify = set(relationships.keys()).intersection(datum_keys_with_skipped_keys)
        for key in relationship_keys_to_modify:
            relationship = relationships[key]
            model = relationship.mapper.class_
            value = model.instance_from(datum[key],
                                        parent=self,
                                        parent_datum=datum,
                                        with_add=with_add,
                                        with_flush=with_flush,
                                        with_no_autoflush=with_no_autoflush)
            if value:
                setattr(self, key, value)

        synonyms = self.__mapper__.synonyms
        synonym_keys_to_modify = set(synonyms.keys()).intersection(datum_keys_with_skipped_keys)
        for key in synonym_keys_to_modify:
            self._try_to_set_attribute(synonyms[key]._proxied_property.columns[0], key, datum[key])

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

        if with_flush:
            Modify.get_db().session.flush()

        return self

    @classmethod
    def _primary_filter_from(model, datum):
        return dict([
            (column.key, dehumanize_if_needed(column, datum.get(column.key)))
            for column in model.__mapper__.primary_key
        ])

    @classmethod
    def _unique_filter_from(model, datum):
        unique_columns = [c for c in model.__mapper__.columns if c.unique]
        for unique_column in unique_columns:
            if unique_column.key in datum:
                unique_value = datum[unique_column.key]
                if unique_value:
                    return { unique_column.key: dehumanize_if_needed(unique_column, unique_value) }

    @classmethod
    def _one_way_foreign_filter_from(model, relationship_model, datum):
        columns = [c for c in model.__mapper__.columns]
        foreign_filter = {}
        for column in columns:
            if column.foreign_keys:
                for foreign_key in column.foreign_keys:
                    key = foreign_key.target_fullname.split('.')[1]
                    if hasattr(relationship_model, key):
                        relationship_column = getattr(relationship_model, key)
                        if relationship_column.foreign_keys:
                            continue
                        if key in datum:
                            value = datum[key]
                            if value is not None:
                                foreign_filter[column.key] = value
        return foreign_filter

    @classmethod
    def _foreign_filter_from(model, relationship_model, datum):
        return {
          **(model._one_way_foreign_filter_from(relationship_model, datum) or {}),
          **(relationship_model._one_way_foreign_filter_from(model, datum) or {})
        }

    @classmethod
    def _instance_from_primaries(model,
                                 datum,
                                 with_add=False,
                                 with_flush=False,
                                 with_no_autoflush=True):
        primary_filter = model._primary_filter_from(datum)
        primary_values = primary_filter.values()
        if all(primary_values):
            if with_no_autoflush:
                with Modify.get_db().session.no_autoflush:
                    instance = model.query.get(primary_values)
            else:
                instance = model.query.get(primary_values)
            if instance:
                return instance.modify(datum,
                                       with_add=with_add,
                                       with_flush=with_flush)

    @classmethod
    def _instance_from_unicity(model,
                               datum,
                               with_add=False,
                               with_flush=False,
                               with_no_autoflush=True):
        unique_filter = model._unique_filter_from(datum)
        if unique_filter:
            if with_no_autoflush:
                with Modify.get_db().session.no_autoflush:
                    instance = model.query.filter_by(**unique_filter).first()
            else:
                instance = model.query.filter_by(**unique_filter).first()
            if instance:
                return instance.modify(datum,
                                       with_add=with_add,
                                       with_flush=with_flush)

    @classmethod
    def _instance_from_search_by_value(model,
                                       datum,
                                       parent=None,
                                       with_add=False,
                                       with_flush=False,
                                       with_no_autoflush=True):
        value_dict = {}
        for (column_name, sub_value) in datum.items():
            column_value = sub_value
            if hasattr(sub_value, 'items') \
                and 'type' in sub_value \
                and sub_value['type'] == '__PARENT__':
                column_value = getattr(parent, sub_value['key'])
                if 'humanized' in sub_value and sub_value['humanized']:
                    column_value = humanize(column_value)
            value_dict[column_name] = column_value
        return model.create_or_modify(value_dict,
                                      with_add=with_add,
                                      with_flush=with_flush,
                                      with_no_autoflush=with_no_autoflush)

    @classmethod
    def _datum_with_search_by_from_foreigns(model,
                                            datum,
                                            parent=None,
                                            parent_datum=None):
        search_filter = {}
        if parent and parent_datum:
            parent_filter = model._foreign_filter_from(parent.__class__,
                                                       parent_datum)
            if parent_filter:
                search_filter.update(parent_filter)

        for relationship in model.__mapper__.relationships:
            if relationship.key in datum:
                relationship_filter = model._foreign_filter_from(relationship.mapper.class_,
                                                                             datum[relationship.key])
                if relationship_filter:
                    search_filter.update(relationship_filter)

        if search_filter:
            unique_columns = [c for c in model.__mapper__.columns if c.unique]
            for unique_column in unique_columns:
                if unique_column.key in search_filter:
                    search_filter = { unique_column.key: search_filter[unique_column.key] }

            return { **datum,
                     **search_filter,
                     '__SEARCH_BY__': list(search_filter.keys())}

    @classmethod
    def _instance_from_foreigns(model,
                                datum,
                                parent=None,
                                parent_datum=None,
                                with_add=False,
                                with_flush=False,
                                with_no_autoflush=True):
        datum = model._datum_with_search_by_from_foreigns(datum,
                                                          parent=parent,
                                                          parent_datum=parent_datum)
        if datum:
            return model._instance_from_search_by_value(datum,
                                                        parent=parent,
                                                        with_add=with_add,
                                                        with_flush=with_flush,
                                                        with_no_autoflush=with_no_autoflush)

    @classmethod
    def instance_from(model,
                      value,
                      parent=None,
                      parent_datum=None,
                      with_add=False,
                      with_flush=False,
                      with_no_autoflush=True):
        if not isinstance(value, model):
            if hasattr(value, 'items'):
                if '__SEARCH_BY__' in value:
                    return model._instance_from_search_by_value(value,
                                                                parent=parent,
                                                                with_add=with_add,
                                                                with_flush=with_flush,
                                                                with_no_autoflush=with_no_autoflush)
                instance = model._instance_from_foreigns(value,
                                                         parent=parent,
                                                         parent_datum=parent_datum,
                                                         with_add=with_add,
                                                         with_flush=with_flush,
                                                         with_no_autoflush=with_no_autoflush)
                if not instance:
                    instance = model._instance_from_primaries(value,
                                                              with_add=with_add,
                                                              with_flush=with_flush,
                                                              with_no_autoflush=with_no_autoflush)
                if not instance:
                    instance = model._instance_from_unicity(value,
                                                            with_add=with_add,
                                                            with_flush=with_flush,
                                                            with_no_autoflush=with_no_autoflush)
                if instance:
                    return instance

                entity = model(**model._created_from(value))
                if with_add:
                    Modify.add(entity)
                if with_flush:
                    Modify.get_db().session.flush()
                return entity

            if hasattr(value, '__iter__'):
                return [
                    model.instance_from(obj,
                                        parent=parent,
                                        parent_datum=parent_datum,
                                        with_add=with_add,
                                        with_flush=with_flush,
                                        with_no_autoflush=with_no_autoflush)
                    for obj in value
                ]
        return value

    def _try_to_set_attribute(self, column, key, value):
        value = dehumanize_if_needed(column, value)
        if isinstance(value, str):
            if isinstance(column.type, Integer):
                self._try_to_set_attribute_with_decimal_value(column, key, value, 'integer')
            elif isinstance(column.type, (Float, Numeric)):
                self._try_to_set_attribute_with_decimal_value(column, key, value, 'float')
            elif isinstance(column.type, DateTime):
                self._try_to_set_attribute_with_deserialized_datetime(column, key, value)
            elif isinstance(column.type, String):
                setattr(self, key, value)
            elif isinstance(column.type, UUID):
                self._try_to_set_attribute_with_uuid(column, key, value)
        elif not isinstance(value, datetime) and isinstance(column.type, DateTime):
            self._try_to_set_attribute_with_deserialized_datetime(column, key, value)
        else:
            setattr(self, key, value)

    def _try_to_set_attribute_with_deserialized_datetime(self, col, key, value):
        try:
            datetime_value = date_helper.to_datetime(value)
            if not datetime_value:
                raise TypeError('Invalid value for %s: %r' % (key, value), 'datetime', key)
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
            unique_filter = model._unique_filter_from(datum)
            if unique_filter:
                return unique_filter
            return model._primary_filter_from(datum)

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
            seq = Sequence(f'{model.__tablename__}_{model.id.property.key}_seq')
            created['id'] = humanize(db.session.execute(seq))
        return created

    @classmethod
    def _existing_from(model, datum):
        existing = {**datum}
        if 'id' in existing and existing['id'] == '__NEXT_ID_IF_NOT_EXISTS__':
            del existing['id']
        return existing

    @classmethod
    def find(model,
             datum,
             with_no_autoflush=True):
        filters = model._filter_from(datum)
        if not filters:
            search_by = datum['__SEARCH_BY__']
            errors = EmptyFilterError()
            filters = ', '.join(search_by) if isinstance(search_by, list) else search_by
            errors.add_error('_filter_from', 'None of filters found among: ' + filters)
            raise errors

        if with_no_autoflush:
            with Modify.get_db().session.no_autoflush:
                entity = model.query.filter_by(**filters).first()
        else:
            entity = model.query.filter_by(**filters).first()

        if not entity:
            return None
        return entity

    @classmethod
    def find_or_create(model,
                       datum,
                       with_add=False,
                       with_flush=False,
                       with_no_autoflush=True):
        entity = model.find(datum, with_no_autoflush=with_no_autoflush)
        if entity:
            return entity
        entity = model(**model._created_from(datum))
        if with_add:
            Modify.add(entity)
        if with_flush:
            Modify.get_db().session.flush()
        return entity

    @classmethod
    def find_and_modify(model,
                        datum,
                        with_add=False,
                        with_flush=False,
                        with_no_autoflush=True):
        entity = model.find(datum,
                            with_no_autoflush=with_no_autoflush)
        if not entity:
            errors = ResourceNotFoundError()
            filters = model._filter_from(datum)
            errors.add_error('find_and_modify', 'No ressource found with {} '.format(json.dumps(filters)))
            raise errors
        return model.modify(entity,
                            model._existing_from(datum),
                            with_add=with_add,
                            with_flush=with_flush)

    @classmethod
    def create_or_modify(model,
                         datum,
                         with_add=False,
                         with_flush=False,
                         with_no_autoflush=True):
        nesting_datum = nesting_datum_from(datum)
        entity = model.find(nesting_datum,
                            with_no_autoflush=with_no_autoflush)
        if entity:
            return model.modify(entity,
                                model._existing_from(nesting_datum),
                                with_add=with_add,
                                with_flush=with_flush,
                                with_no_autoflush=with_no_autoflush)
        entity = model(**model._created_from(nesting_datum))
        if with_add:
            Modify.add(entity)
        if with_flush:
            Modify.get_db().session.flush()
        return entity
