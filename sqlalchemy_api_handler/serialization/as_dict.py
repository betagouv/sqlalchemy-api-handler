from collections import OrderedDict
from functools import partial, singledispatch
from typing import Callable, Iterable, Set, List
from sqlalchemy.orm.collections import InstrumentedList

from sqlalchemy_api_handler.api_handler import ApiHandler
from sqlalchemy_api_handler.serialization.serialize import serialize
from sqlalchemy_api_handler.utils.asynchronous import async_map as default_async_map


def exclusive_includes_from(entity, includes):
    exclusive_includes = includes.copy()
    for column_key in entity.__mapper__.columns.keys():
        if column_key not in includes:
            exclusive_includes.append('-{}'.format(column_key))
    return exclusive_includes


@singledispatch
def as_dict(value,
            column=None,
            async_map=None,
            includes=None,
            mode=None,
            use_async=False):
    return serialize(value, column=column)


@as_dict.register(InstrumentedList)
def as_dict_for_intrumented_list(entities,
                                 column=None,
                                 async_map: Callable=None,
                                 includes: Iterable = None,
                                 mode: str = 'columns-and-includes',
                                 use_async: bool=False):
    if async_map is None:
        async_map = default_async_map
    not_deleted_entities = filter(lambda x: not x.is_soft_deleted(), entities)
    dictify = partial(as_dict,
                      async_map=async_map,
                      includes=includes,
                      mode=mode)
    map_method = async_map if use_async else map
    return list(map_method(dictify, not_deleted_entities))


@as_dict.register(ApiHandler)
def as_dict_for_api_handler(entity,
                            column=None,
                            async_map: Callable=None,
                            includes: Iterable=None,
                            mode: str='columns-and-includes',
                            use_async: bool=False):
    result = OrderedDict()

    if includes is None and hasattr(entity, '__as_dict_includes__'):
        includes = entity.__as_dict_includes__
    if mode == 'only-includes':
        includes = exclusive_includes_from(entity, includes)

    for key in _keys_to_serialize(entity, includes):
        use_async = key.startswith('|')
        if use_async:
            key = key[1:]
        value = getattr(entity, key)
        columns = entity.__mapper__.columns
        column = columns.get(key)
        if column is None:
            synonym = entity.__mapper__.synonyms.get(key)
            if synonym:
                column = synonym._proxied_property.columns[0]
        result[key] = as_dict(value,
                              async_map=async_map,
                              column=column)

    for join in _joins_to_serialize(includes):
        key = join['key']
        use_async = key.startswith('|')
        if use_async:
            key = key[1:]
        sub_includes = join.get('includes')
        sub_mode = join.get('mode', mode)
        value = getattr(entity, key)
        result[key] = as_dict(value,
                              async_map=async_map,
                              includes=sub_includes,
                              mode=sub_mode,
                              use_async=use_async)

    return result

def _joins_to_serialize(includes: Iterable=None) -> List[dict]:
    if includes is None:
        includes = ()
    dict_joins = filter(lambda include: isinstance(include, dict), includes)
    return list(dict_joins)


def _keys_to_serialize(entity, includes: Iterable=None) -> Set[str]:
    all_keys = entity.__mapper__.columns.keys()
    return set(all_keys).union(_included_keys(includes)) - _excluded_keys(includes)


def _included_keys(includes: Iterable=None) -> Set[str]:
    if includes is None:
        includes = ()
    string_includes = filter(lambda include: isinstance(include, str), includes)
    included_keys = filter(lambda string_include: not string_include.startswith('-'), string_includes)
    return set(included_keys)


def _excluded_keys(includes: Iterable=None):
    if includes is None:
        includes = ()
    string_includes = filter(lambda include: isinstance(include, str), includes)
    excluded_keys = filter(lambda string_include: string_include.startswith('-'), string_includes)
    cleaned_excluded_keys = map(lambda excluded_key: excluded_key[1:], excluded_keys)
    return set(cleaned_excluded_keys)
