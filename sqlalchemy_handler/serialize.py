from datetime import datetime
import enum
from psycopg2.extras import DateTimeRange
import sqlalchemy

from sqlalchemy_handler.date import DateTimes


def format_into_ISO_8601(value):
    return value.isoformat() + "Z"

def serialize(value, **options):
    if isinstance(value, sqlalchemy.Enum):
        return value.name
    elif isinstance(value, enum.Enum):
        return value.value
    elif isinstance(value, datetime):
        return format_into_ISO_8601(value)
    elif isinstance(value, DateTimeRange):
        return {
            'start': value.lower,
            'end': value.upper
        }
    elif isinstance(value, list)\
            and len(value) > 0\
            and isinstance(value[0], DateTimeRange):
        return list(map(lambda d: {'start': d.lower,
                                   'end': d.upper},
                        value))
    elif isinstance(value, DateTimes):
        return [format_into_ISO_8601(v) for v in value.datetimes]

    else:
        return value
