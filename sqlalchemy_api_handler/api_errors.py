import json
import re


class ApiErrors(Exception):
    def __init__(self, errors: dict = None):
        self.errors = errors if errors else {}

    def add_error(self, field, error):
        if field in self.errors:
            self.errors[field].append(error)
        else:
            self.errors[field] = [error]

    def check_date(self, field, value):
        if isinstance(value, (str, unicode)) and re.search('^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$', value):
            return True
        else:
            self.add_error(field, 'format is invalid')

    def check_email(self, field, value):
        if not "@" in value:
            self.add_error(field, 'L\'e-mail doit contenir un @.')

    def check_float(self, field, value):
        if isinstance(value, float) or \
           (isinstance(value, (str, unicode)) and re.search('^\d+(\.\d*|)$', value)):
            return True
        else:
            self.add_error(field, 'value must be a number.')

    def check_min_length(self, field, value, length):
        if len(value) < length:
            self.add_error(field, 'value should be long at least of ' + str(length) + ' characters.')

    def maybe_raise(self):
        if len(self.errors) > 0:
            raise self

    def __str__(self):
        if self.errors:
            return json.dumps(self.errors, indent=2)

    status_code = None
