from datetime import datetime
from decimal import Decimal, \
                    InvalidOperation
from sqlalchemy import DateTime, \
                       Float, \
                       Integer, \
                       Numeric, \
                       String

from sqlalchemy_handler.api_errors import DateTimeCastError, \
                                          DecimalCastError
from sqlalchemy_handler.as_dict import AsDict
from sqlalchemy_handler.date import deserialize_datetime
from sqlalchemy_handler.delete import Delete
from sqlalchemy_handler.human_ids import dehumanize
from sqlalchemy_handler.soft_delete import SoftDelete


class Populate(
        AsDict,
        Delete,
        SoftDelete
):
    def __init__(self, **options):
        if options and 'from_dict' in options and options['from_dict']:
            self.populateFromDict(options['from_dict'])

    def populateFromDict(self, dct, skipped_keys=[]):
        self.check_not_soft_deleted()

        data = dct.copy()

        if data.__contains__('id'):
            del data['id']

        cols = self.__class__.__table__.columns._data

        for key in data.keys():

            data_value = data.get(key)

            if (key == 'deleted') or (key in skipped_keys):
                continue

            if cols.__contains__(key):
                col = cols[key]

                if self.is_relationship_item(key, data_value):
                    value = dehumanize(data_value)
                    setattr(self, key, value)
                    continue

                value = data_value

                value_is_string = isinstance(value, str)

                if value_is_string and isinstance(col.type, Integer):
                    try:
                        setattr(self, key, Decimal(value))
                        continue
                    except InvalidOperation:
                        error = DecimalCastError()
                        error.addError(col.name, "Invalid value for {} ({}): '{}'".format(key, 'integer', value))
                        raise error

                elif value_is_string and isinstance(col.type, (Float, Numeric)):
                    try:
                        setattr(self, key, Decimal(value))
                        continue
                    except InvalidOperation:
                        error = DecimalCastError()
                        error.addError(col.name, "Invalid value for {} ({}): '{}'".format(key, 'float', value))
                        raise error

                elif not isinstance(value, datetime) and isinstance(col.type, DateTime):
                    try:
                        datetime_value = deserialize_datetime(key, value)
                        if not datetime_value:
                            raise TypeError('Invalid value for %s: %r' % (key, value), 'datetime', key)
                        setattr(self, key, datetime_value)
                        continue
                    except TypeError:
                        error = DateTimeCastError()
                        error.addError(col.name, "Invalid value for %s (datetime): %r" % (key, value))
                        raise error

                elif value_is_string and isinstance(col.type, String):
                    setattr(self, key, value.strip() if value else value)
                    continue

                setattr(self, key, value)
