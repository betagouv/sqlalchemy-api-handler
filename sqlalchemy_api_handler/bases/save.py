from sqlalchemy.exc import DataError, IntegrityError, InternalError

from sqlalchemy_api_handler.api_errors import ApiErrors
from sqlalchemy_api_handler.bases.errors import Errors
from sqlalchemy_api_handler.bases.modify import Modify


class Save(Modify, Errors):

    @staticmethod
    def save(*entities):
        if not entities:
            return None

        db = Save.get_db()

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

        # COMMIT
        try:
            db.session.commit()
        except DataError as de:
            api_errors.add_error(*Errors.restize_data_error(de))
            db.session.rollback()
            raise api_errors
        except IntegrityError as ie:
            api_errors.add_error(*Errors.restize_integrity_error(ie))
            db.session.rollback()
            raise api_errors
        except InternalError as ie:
            for entity in entities:
                api_errors.add_error(*entity.restize_internal_error(ie))
            db.session.rollback()
            raise api_errors
        except TypeError as te:
            api_errors.add_error(*Errors.restize_type_error(te))
            db.session.rollback()
            raise api_errors
        except ValueError as ve:
            api_errors.add_error(*Errors.restize_value_error(ve))
            db.session.rollback()
            raise api_errors

        if api_errors.errors.keys():
            raise api_errors
