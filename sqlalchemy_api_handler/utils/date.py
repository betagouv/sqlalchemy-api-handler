from datetime import datetime

DATE_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def format_into_ISO_8601(value):
    return value.isoformat() + "Z"


class DateTimes:
    def __init__(self, *datetimes):
        self.datetimes = list(datetimes)

    def __eq__(self, other):
        return self.datetimes == other.datetimes


def to_datestring(date, date_format=DATE_ISO_FORMAT):
    if not date:
        return None
    return date.strftime(date_format)


def to_datetime(date: str, date_format=DATE_ISO_FORMAT):
    if date is None:
        return None

    valid_patterns = [date_format,
                      date_format.replace('.%fZ', ''),
                      date_format.replace('.%fZ', '.%f'),
                      date_format.replace('.%fZ', 'Z')]
    for pattern in valid_patterns:
        try:
            return datetime.strptime(date, pattern)
        except ValueError as e:
            continue
