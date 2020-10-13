import enum
from datetime import datetime
from functools import singledispatch
import sqlalchemy
from psycopg2._range import DateTimeRange
from sqlalchemy import Integer

from sqlalchemy_api_handler.utils.date import DateTimes, format_into_ISO_8601
from sqlalchemy_api_handler.utils.humanize import humanize
from sqlalchemy_api_handler.utils.is_id_column import is_id_column


@singledispatch
def serialize(value, column=None):
    return value


@serialize.register(int)
def _(value, column=None):
    if is_id_column(column):
        return humanize(value)
    return value


@serialize.register(sqlalchemy.Enum)
def _(value, column=None):
    return value.name


@serialize.register(enum.Enum)
def _(value, column=None):
    return value.value


@serialize.register(datetime)
def _(value, column=None):
    return format_into_ISO_8601(value)


@serialize.register(DateTimeRange)
def _(value, column=None):
    return {'start': value.lower, 'end': value.upper}


@serialize.register(bytes)
def _(value, column=None):
    return list(value)


@serialize.register(list)
def _(value, column=None):
    return list(map(serialize, value))


@serialize.register(DateTimes)
def _(value, column=None):
    return [format_into_ISO_8601(v) for v in value.datetimes]
