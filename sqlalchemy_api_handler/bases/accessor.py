import inflect
import inspect
from sqlalchemy.orm.attributes import InstrumentedAttribute


class Accessor():
    @classmethod
    def get_db(cls):
        return Accessor.db

    @classmethod
    def set_db(cls, db):
        Accessor.db = db

    @classmethod
    def model_from_table_name(cls, table_name):
        for model in Accessor.get_db().Model._decl_class_registry.values():
            if not hasattr(model, '__table__'):
                continue
            if model.__tablename__ == table_name:
                return model

    @classmethod
    def model_from_plural_name(cls, plural_name):
        return Accessor.model_from_table_name(inflect.engine().singular_noun(plural_name))

    @classmethod
    def instrumented_attributes_from_model_name(model_name):
        return inspect.getmembers(Accessor.model_from_table_name(model_name),
                                  lambda p: isinstance(p, InstrumentedAttribute))
