import inspect

from sqlalchemy_api_handler.bases.errors import NotSoftDeletableMixinException, \
                                                SoftDeletedRecordException


class SoftDelete():

    def __init__(self):
        self.isSoftDeleted = False

    def check_not_soft_deleted(self):
        if self.is_soft_deleted():
            api_errors = SoftDeletedRecordException()
            api_errors.add_error('check_not_soft_deleted', 'Entity already soft deleted')
            raise api_errors

    def is_soft_deleted(self):
        classes = inspect.getmro(type(self))
        if 'SoftDeletableMixin' in [cl.__name__ for cl in classes]:
            return self.isSoftDeleted
        return False

    @staticmethod
    def soft_delete(*entities):
        for entity in entities:
            classes = inspect.getmro(type(entity))
            if 'SoftDeletableMixin' not in [cl.__name__ for cl in classes]:
                api_errors = NotSoftDeletableMixinException()
                api_errors.add_error('soft_delete', 'cannot soft delete this entity')
                raise api_errors
            entity.isSoftDeleted = True
