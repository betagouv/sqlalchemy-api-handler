from collections import OrderedDict
from functools import singledispatch
from typing import Iterable, Set, List
from sqlalchemy.orm.collections import InstrumentedList

from sqlalchemy_api_handler.api_handler import ApiHandler
from sqlalchemy_api_handler.serialization.serialize import serialize

@singledispatch
def as_dict(value, column=None, includes=None):
    return serialize(value, column=column)


@as_dict.register(InstrumentedList)
def as_dict_for_intrumented_list(objs, column=None, includes: Iterable = None):
    not_deleted_objs = filter(lambda x: not x.is_soft_deleted(), objs)
    return [as_dict(obj, includes=includes) for obj in not_deleted_objs]


@as_dict.register(ApiHandler)
def as_dict_for_api_handler(obj,
                            column=None,
                            includes: Iterable = None):
    result = OrderedDict()

    if includes is None and hasattr(obj, '__as_dict_includes__'):
        includes = obj.__as_dict_includes__

    for key in _keys_to_serialize(obj, includes):
        value = getattr(obj, key)
        columns = obj.__mapper__.columns
        column = columns.get(key)
        if column is None:
            synonym = obj.__mapper__.synonyms.get(key)
            if synonym:
                column = synonym._proxied_property.columns[0]
        result[key] = as_dict(value, column=column)

    for join in _joins_to_serialize(includes):
        key = join['key']
        sub_includes = join.get('includes')
        value = getattr(obj, key)
        result[key] = as_dict(value, includes=sub_includes)

    return result

def _joins_to_serialize(includes: Iterable = None) -> List[dict]:
    if includes is None:
        includes = ()
    dict_joins = filter(lambda include: isinstance(include, dict), includes)
    return list(dict_joins)


def _keys_to_serialize(obj, includes: Iterable=None) -> Set[str]:
    all_keys = obj.__mapper__.columns.keys()
    return set(all_keys).union(_included_keys(includes)) - _excluded_keys(includes)


def _included_keys(includes: Iterable = None) -> Set[str]:
    if includes is None:
        includes = ()
    string_includes = filter(lambda include: isinstance(include, str), includes)
    included_keys = filter(lambda string_include: not string_include.startswith('-'), string_includes)
    return set(included_keys)


def _excluded_keys(includes: Iterable = None):
    if includes is None:
        includes = ()
    string_includes = filter(lambda include: isinstance(include, str), includes)
    excluded_keys = filter(lambda string_include: string_include.startswith('-'), string_includes)
    cleaned_excluded_keys = map(lambda excluded_key: excluded_key[1:], excluded_keys)
    return set(cleaned_excluded_keys)
