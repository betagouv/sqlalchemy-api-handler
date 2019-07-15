import json

class ApiErrors(Exception):
    def __init__(self):
        self.errors = {}

    def addError(self, field, error):
        self.errors[field] = self.errors[field].append(error)\
                                if field in self.errors\
                                else [error]

    def checkDate(self, field, value):
        if (isinstance(value, str) or isinstance(value, unicode)) and re.search('^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$', value):
            return True
        else:
            self.addError(field, 'format is invalid')

    def checkFloat(self, field, value):
        if isinstance(value, float) or \
           ((isinstance(value, str) or isinstance(value, unicode)) and re.search('^\d+(\.\d*|)$', value)):
            return True
        else:
            self.addError(field, 'value must be a number.')

    def checkWithin(self, field, value, min, max):
        self.checkUnder(field, value, max)
        self.checkOver(field, value, min)

    def checkOver(self, field, value, min):
        if value>min:
            return True
        else:
            self.addError(field, 'value should be greater than '+str(min))

    def checkUnder(self, field, value, max):
        if value<min:
            return True
        else:
            self.addError(field, 'value should be less than '+str(min))

    def checkMinLength(self, field, value, length):
        if len(value)<length:
            self.addError(field, 'You need to enter ' + str(length) + ' characters.')

    def checkEmail(self, field, value):
        if not "@" in value:
            self.addError(field, 'The email should have @.')

    def maybeRaise(self):
        if len(self.errors)>0:
            raise self

    def __str__(self):
        if self.errors:
            return json.dumps(self.errors, indent=2)

    status_code = None

class ResourceGoneError(ApiErrors):
    pass


class ResourceNotFound(ApiErrors):
    pass


class ForbiddenError(ApiErrors):
    pass


class DecimalCastError(ApiErrors):
    pass


class DateTimeCastError(ApiErrors):
    pass
