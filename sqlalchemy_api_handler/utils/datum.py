from sqlalchemy_api_handler.utils.dehumanize import dehumanize
from sqlalchemy_api_handler.utils.humanize import humanize
from sqlalchemy_api_handler.utils.is_id_column import is_id_column


def dehumanize_ids_in(datum, model):
    if not datum:
        return None
    dehumanized_datum = {**datum}
    for (key, value) in datum.items():
        if hasattr(model, key):
            if is_id_column(getattr(model, key)):
                dehumanized_datum[key] = dehumanize(value)
    return dehumanized_datum


def humanize_ids_in(datum, model):
    if not datum:
        return None
    humanized_datum = {**datum}
    for (key, value) in datum.items():
        if hasattr(model, key):
            if is_id_column(getattr(model, key)):
                humanized_datum[key] = humanize(value)
    return humanized_datum


def synonyms_in(datum, model):
    synonymized_datum = {**datum}
    for synonym in model.__mapper__.synonyms:
        column_key = synonym._proxied_property.columns[0].key
        if column_key in synonymized_datum:
            synonymized_datum[synonym.key] = synonymized_datum[column_key]
            del synonymized_datum[column_key]
    return synonymized_datum


def columns_in(datum, model):
    columnized_datum = {**datum}
    for synonym in model.__mapper__.synonyms:
        column_key = synonym._proxied_property.columns[0].key
        if synonym.key in columnized_datum:
            columnized_datum[column_key] = columnized_datum[synonym.key]
            del columnized_datum[synonym.key]
    return columnized_datum


def merge(source, destination):
    '''
    run me with nosetests --with-doctest file.py

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    '''
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


def nesting_datum_from(flatten_path_datum,
                       nested_data_by_prefix=None):
    datum = {}
    if nested_data_by_prefix is None:
        nested_data_by_prefix = {}
    for (key, value) in flatten_path_datum.items():
        if '.' in key:
            chunks = key.split('.')
            prefix = chunks[0]
            index = int(chunks[1]) if chunks[1].isdigit() else None
            if prefix not in nested_data_by_prefix:
                nested_data_by_prefix[prefix] = [] if index != None else {}
            if index != None:
                next_key = '.'.join(chunks[2:])

                is_new = len(nested_data_by_prefix[prefix]) < index + 1

                next_value = nesting_datum_from({ next_key: value },
                                                nested_data_by_prefix=nested_data_by_prefix[prefix][index] if not is_new else None)
                if is_new:
                    nested_data_by_prefix[prefix].insert(index, next_value)
                else:
                    merged = merge(nested_data_by_prefix[prefix][index], next_value)
                    nested_data_by_prefix[prefix][index] = merged
            else:
                next_key = '.'.join(chunks[1:])
                next_value = nesting_datum_from({ next_key: value },
                                                nested_data_by_prefix=nested_data_by_prefix[prefix])
                nested_data_by_prefix[prefix].update(next_value)
        else:
            if key == '__SEARCH_BY__' and  ',' in value:
                value = value.split(',')
            datum[key] = value
    return {**datum, **nested_data_by_prefix}


def relationships_in(datum, model):
    relationed_datum = {**datum}
    for (key, relationship) in model.__mapper__.relationships.items():
        activity_identifier_key = '{}ActivityIdentifier'.format(key)
        if activity_identifier_key in relationed_datum:
            model = relationship.mapper.class_
            instance = model.query.filter_by(activityIdentifier=relationed_datum[activity_identifier_key]) \
                                  .one()
            relationed_datum[key] = instance
    return relationed_datum



def old_data_from(entity, activity):
    if activity.verb == 'insert':
        return activity.changed_data
    if activity.old_data:
        return activity.old_data
    return entity.just_before_activity_from(activity).data


def merged_datum_from_activities(entity,
                                 activities,
                                 initial=None):
    merged_datum = {}
    old_data = old_data_from(entity, activities[0])
    for activity in activities:
        activity.old_data = old_data
        activity.verb = 'update'
        old_data = { **old_data,
                     **activity.changed_data }
        merged_datum = { **merged_datum,
                         **relationships_in(activity.patch, entity.__class__) }
    return merged_datum
