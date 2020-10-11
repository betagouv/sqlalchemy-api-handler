from compose import compose
import json
from sqlalchemy import String
from sqlalchemy.sql.expression import and_
from flask import current_app as app, jsonify
from sqlalchemy_api_handler import ApiHandler, as_dict

INDEXES = range(0, 10)

@compose(app.manager.option('-m',
                            '--model',
                            help='model name'),
         *[app.manager.option('-i{}'.format(index),
                              '--item{}'.format(index),
                              help='item that filters')
           for index in INDEXES])
def filter(**kwargs):
    model = ApiHandler.model_from_name(kwargs['model'].title())
    query_filters = []
    for index in INDEXES:
        item = kwargs['item{}'.format(index)]
        if not item:
            continue
        (key, value) = kwargs['item{}'.format(index)].split(',')
        if '.' in key:
            keys = key.split('.')
            left_value = getattr(model, keys[0])
            for other_key in keys[1:]:
                left_value = left_value[other_key]
            left_value = left_value.astext.cast(String)
        else:
            left_value = getattr(model, key)
        query_filters.append(left_value == value)
    entities = model.query.filter(and_(*query_filters)).all()

    response = jsonify([as_dict(entity) for entity in entities])
    dumps = json.dumps(response.json, indent=2, sort_keys=True)
    print(dumps)
