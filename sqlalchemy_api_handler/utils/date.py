from datetime import datetime

def match_format(value: str, format: str):
    try:
        datetime.strptime(value, format)
    except ValueError:
        return False
    else:
        return True


def deserialize_datetime(key, value):
    valid_patterns = ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']
    datetime_value = None

    for pattern in valid_patterns:
        if match_format(value, pattern):
            datetime_value = datetime.strptime(value, pattern)

    return datetime_value


def format_into_ISO_8601(value):
    return value.isoformat() + "Z"


class DateTimes:
    def __init__(self, *datetimes):
        self.datetimes = list(datetimes)

    def __eq__(self, other):
        return self.datetimes == other.datetimes
