from sqlalchemy_handler.db import db

class Delete():

    def delete(self):
        db.session.delete(self)
        return self

    @staticmethod
    def delete_objects(*objects):
        delete_objects = list(map(Delete.delete, objects))
        return delete_objects
