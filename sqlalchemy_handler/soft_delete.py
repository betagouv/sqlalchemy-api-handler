import inspect

class NotSoftDeletableMixinException(Exception):
    pass

class SoftDeletedRecordException(Exception):
    pass

class SoftDelete():

    def __init__(self):
        self.isSoftDeleted = False

    def check_not_soft_deleted(self):
        if self.is_soft_deleted():
            raise SoftDeletedRecordException

    def is_soft_deleted(self):
        classes = inspect.getmro(type(self))
        if 'SoftDeletableMixin' in [cl.__name__ for cl in classes]:
            return self.isSoftDeleted
        return False

    def soft_delete(self):
        classes = inspect.getmro(type(self))
        if 'SoftDeletableMixin' not in [cl.__name__ for cl in classes]:
            raise NotSoftDeletableMixinException
        self.isSoftDeleted = True
        return self

    @staticmethod
    def soft_delete_objects(*objects):
        return list(map(SoftDelete.soft_delete, objects))
