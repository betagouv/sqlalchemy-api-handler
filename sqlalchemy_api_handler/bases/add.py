from sqlalchemy_api_handler.api_errors import ApiErrors
from sqlalchemy_api_handler.bases.accessor import Accessor
from sqlalchemy_api_handler.bases.errors import Errors


class Add(Accessor, Errors):

    @staticmethod
    def add(*entities):
        if not entities:
            return None

        db = Add.get_db()

        # CUMULATE ERRORS IN ONE SINGLE API ERRORS DURING ADD TIME
        api_errors = ApiErrors()
        for entity in entities:
            with db.session.no_autoflush:
                entity_api_errors = entity.errors()
            if entity_api_errors.errors.keys():
                api_errors.errors.update(entity_api_errors.errors)
            else:
                db.session.add(entity)

        # CHECK BEFORE COMMIT
        if api_errors.errors.keys():
            raise api_errors

        return api_errors
