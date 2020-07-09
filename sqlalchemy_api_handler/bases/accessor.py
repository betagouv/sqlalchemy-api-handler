import inflect


class Accessor():
    @classmethod
    def get_db(cls):
        return Accessor.db

    @classmethod
    def set_db(cls, db):
        Accessor.db = db

    @classmethod
    def model_with_table_name(cls, table_name):
        for model in Accessor.get_db().Model._decl_class_registry.values():
            if not hasattr(model, '__table__'):
                continue
            if model.__tablename__ == table_name:
                return model

    @classmethod
    def model_with_plural_name(cls, plural_name):
        return Accessor.model_with_table_name(inflect.engine().singular_noun(plural_name))
