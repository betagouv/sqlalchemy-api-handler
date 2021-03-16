import inflect

from sqlalchemy_api_handler.bases.errors import GetPathError


class Accessor():

    def get(self,
            path,
            with_get_path_error=True):
        if '.' in path:
            chunks = path.split('.')
            key = chunks[0]
            value = getattr(self, key)
            if chunks[1].isdigit():
                value = value[int(chunks[1])]
                if len(chunks) == 2:
                    return value
                else:
                    next_path = '.'.join(chunks[2:])
            else:
                next_path = '.'.join(chunks[1:])
            if value:
                return value.get(next_path, with_get_path_error=with_get_path_error)
            if with_get_path_error:
                errors = GetPathError()
                errors.add_error('path', f'This path {path} returns a None with entity {str(self)} at key {key}')
                raise errors
            return None

        return getattr(self, path)

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
