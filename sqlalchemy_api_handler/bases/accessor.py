import inflect

from sqlalchemy_api_handler.bases.errors import GetPathError


class Accessor():

    def get(self,
            path,
            with_get_path_error=True):

        is_direct_attribute_key =  '.' not in path
        if is_direct_attribute_key:
            return getattr(self, path)

        chunks = path.split('.')
        key = chunks[0]
        value = getattr(self, key)

        child_key = chunks[1]
        start_index_for_child_path = 1
        child_key_is_index = child_key.isdigit()
        if child_key_is_index:
            value = value[int(child_key)]
            path_is_direct_a_get_of_child_element = len(chunks) == 2
            if path_is_direct_a_get_of_child_element:
                return value
            start_index_for_child_path = 2

        child_path = '.'.join(chunks[start_index_for_child_path:])

        if value is not None:
            return value.get(child_path, with_get_path_error=with_get_path_error)

        if with_get_path_error:
            errors = GetPathError()
            errors.add_error('path', f'This path {path} returns a None with entity {str(self)} at key {key}')
            raise errors

        return None

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
