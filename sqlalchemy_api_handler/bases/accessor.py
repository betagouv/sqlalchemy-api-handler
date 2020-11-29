import inflect


class Accessor():
    @classmethod
    def get_db(cls):
        return Accessor.db

    @classmethod
    def set_db(cls, db):
        Accessor.db = db

    @classmethod
    def models(cls):
        return [
            v for v in Accessor.get_db().Model._decl_class_registry.values()
            if hasattr(v, '__table__')
        ]

    @classmethod
    def model_from_name(cls, name):
        for model in cls.models():
            if model.__name__ == name:
                return model

    @classmethod
    def model_from_table_name(cls, table_name):
        for model in Accessor.models():
            if model.__tablename__ == table_name:
                return model

    @classmethod
    def model_from_plural_name(cls, plural_name):
        return Accessor.model_from_table_name(inflect.engine().singular_noun(plural_name))
