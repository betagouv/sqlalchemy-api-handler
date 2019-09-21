class Accessor():
    @classmethod
    def get_db(cls):
        return Accessor.db

    @classmethod
    def set_db(cls, db):
        Accessor.db = db
