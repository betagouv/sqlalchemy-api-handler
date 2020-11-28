import re
import traceback
from sqlalchemy.exc import DataError
from sqlalchemy import CHAR, \
                       Column,\
                       Enum,\
                       Float,\
                       Integer,\
                       String

from sqlalchemy_api_handler.api_errors import ApiErrors
from sqlalchemy_api_handler.utils.logger import logger

DUPLICATE_KEY_ERROR_CODE = '23505'
NOT_FOUND_KEY_ERROR_CODE = '23503'
OBLIGATORY_FIELD_ERROR_CODE = '23502'


class Errors():

    @staticmethod
    def restize_global_error(e):
        logger.error("UNHANDLED ERROR : ")
        traceback.print_exc()
        return ["global", "Une erreur technique s'est produite. Elle a été notée, et nous allons investiguer au plus vite."]

    @staticmethod
    def restize_data_error(e):
        if e.args and len(e.args) > 0 and e.args[0].startswith('(psycopg2.DataError) value too long for type'):
            max_length = re.search('\(psycopg2.DataError\) value too long for type (.*?) varying\((.*?)\)', e.args[0], re.IGNORECASE).group(2)
            return ['global', "La valeur d'une entrée est trop longue (max " + max_length + ")"]
        return Errors.restize_global_error(e)

    @staticmethod
    def restize_integrity_error(e):
        if hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode == DUPLICATE_KEY_ERROR_CODE:
            field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
            return [field, 'Une entrée avec cet identifiant existe déjà dans notre base de données']
        if hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode == NOT_FOUND_KEY_ERROR_CODE:
            field = re.search('Key \((.*?)\)=', str(e._message), re.IGNORECASE).group(1)
            return [field, 'Aucun objet ne correspond à cet identifiant dans notre base de données']
        if hasattr(e, 'orig') and hasattr(e.orig, 'pgcode') and e.orig.pgcode == OBLIGATORY_FIELD_ERROR_CODE:
            field = re.search('column "(.*?)"', e.orig.pgerror, re.IGNORECASE).group(1)
            return [field, 'Ce champ est obligatoire']
        return Errors.restize_global_error(e)

    @staticmethod
    def restize_internal_error(e):
        return Errors.restize_global_error(e)

    @staticmethod
    def restize_type_error(e):
        if e.args and len(e.args) > 1 and e.args[1] == 'geography':
            return [e.args[2], 'doit etre une liste de nombre décimaux comme par exemple : [2.22, 3.22]']
        if e.args and len(e.args) > 1 and e.args[1] and e.args[1] == 'decimal':
            return [e.args[2], 'doit être un nombre décimal']
        if e.args and len(e.args) > 1 and e.args[1] and e.args[1] == 'integer':
            return [e.args[2], 'doit être un entier']
        return Errors.restize_global_error(e)

    @staticmethod
    def restize_value_error(e):
        if len(e.args)>1 and e.args[1] == 'enum':
            return [e.args[2], ' doit etre dans cette liste : '+",".join(map(lambda x : '"'+x+'"', e.args[3]))]
        return Errors.restize_global_error(e)

    def errors(self):
        api_errors = ApiErrors()
        data = self.__class__.__table__.columns._data
        for key in data.keys():
            col = data[key]
            val = getattr(self, key)
            if not isinstance(col, Column):
                continue
            if not col.nullable\
               and not col.foreign_keys\
               and not col.primary_key\
               and col.default is None\
               and val is None:
                api_errors.add_error(key, 'Cette information est obligatoire')
            if val is None:
                continue
            if isinstance(col.type, (CHAR, String))\
               and not isinstance(col.type, Enum)\
               and not isinstance(val, str):
                api_errors.add_error(key, 'doit être une chaîne de caractères')
            if isinstance(col.type, (CHAR, String))\
               and isinstance(val, str)\
               and col.type.length\
               and len(val) > col.type.length:
                api_errors.add_error(key,
                                     'Vous devez saisir moins de '
                                     + str(col.type.length)
                                     + ' caractères')
            if isinstance(col.type, Integer)\
               and not isinstance(val, int):
                api_errors.add_error(key, 'doit être un entier')
            if isinstance(col.type, Float)\
               and not isinstance(val, float)\
               and not isinstance(val, int):
                api_errors.add_error(key, 'doit être un nombre')
        return api_errors


class ActivityError(ApiErrors):
    pass


class DateTimeCastError(ApiErrors):
    pass


class DecimalCastError(ApiErrors):
    pass


class EmptyFilterError(ApiErrors):
    pass


class ForbiddenError(ApiErrors):
    pass


class NotSoftDeletableMixinException(ApiErrors):
    pass


class ResourceGoneError(ApiErrors):
    pass


class SoftDeletedRecordException(ApiErrors):
    pass


class ResourceNotFoundError(ApiErrors):
    pass


class UuidCastError(ApiErrors):
    pass
