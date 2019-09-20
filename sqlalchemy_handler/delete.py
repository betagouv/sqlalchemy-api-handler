from sqlalchemy_handler.accessor import Accessor

class Delete(Accessor):

    def delete(self):
        Accessor.get_db().session.delete(self)
        return self

    @staticmethod
    def delete_objects(*objects):
        delete_objects = list(map(Delete.delete, objects))
        return delete_objects
