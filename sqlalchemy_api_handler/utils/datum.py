from sqlalchemy_api_handler.utils.human_ids import dehumanize, \
                                                   humanize, \
                                                   is_id_column


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


def relationships_in(datum, model):
    relationed_datum = {**datum}
    for (key, relationship) in model.__mapper__.relationships.items():
        uuid_key = '{}ActivityUuid'.format(key)
        if uuid_key in relationed_datum:
            model = relationship.mapper.class_
            instance = model.query.filter_by(activityUuid=relationed_datum[uuid_key]) \
                                  .one()
            relationed_datum[key] = instance
    return relationed_datum
