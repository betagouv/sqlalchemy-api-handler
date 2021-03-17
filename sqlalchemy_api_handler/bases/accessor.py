import inflect

from sqlalchemy_api_handler.bases.errors import GetPathError


class Accessor():

    def get(self,
            path,
            with_get_path_error=True):

        if path is None or path == '':
            return None

        if '.' not in path:
            return getattr(self, path)

        chunks = path.split('.')
        key = chunks[0]
        child_key = chunks[1]

        if child_key.isdigit():
            value = getattr(self, key)[int(child_key)]
            child_path = '.'.join(chunks[2:])
            if child_path == '':
                return value
        else:
            value = getattr(self, key)
            child_path = '.'.join(chunks[1:])

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
