from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, synonym

from sqlalchemy_api_handler.bases.errors import ActivityError
from sqlalchemy_api_handler.utils.datum import relationships_in, \
                                               synonyms_in
from sqlalchemy_api_handler.utils.dehumanize import dehumanize_ids_in
from sqlalchemy_api_handler.utils.humanize import humanize, humanize_ids_in


class ActivityMixin(object):
    entityIdentifier = Column(UUID(as_uuid=True))

    @declared_attr
    def dateCreated(cls):
        return synonym('issued_at')

    @declared_attr
    def tableName(cls):
        return synonym('table_name')

    @property
    def datum(self):
        if not self.data:
            return None
        model = self.model
        return synonyms_in(humanize_ids_in(self.data, self.model), model)

    @property
    def model(self):
        return self.__class__.model_from_table_name(self.table_name)

    @property
    def modelName(self):
        return self.model.__name__

    @property
    def entity(self):
        model = self.model
        return model(**self.datum)

    @property
    def oldDatum(self):
        if not self.old_data:
            return None
        model = self.model
        return synonyms_in(humanize_ids_in(self.old_data, model), model)

    @property
    def patch(self):
        if not self.changed_data:
            return None
        model = self.model
        return synonyms_in(humanize_ids_in(self.changed_data, model), model)

    def modify(self,
               datum,
               skipped_keys=[],
               with_add=False):
        dehumanized_datum = {**datum}

        if 'modelName' in datum:
            model = self.__class__.model_from_name(datum['modelName'])
            if 'tableName' in datum:
                if datum['tableName'] != model.__tablename__:
                    errors = ActivityError()
                    errors.add_error('modelName', '{} different from {}'.format(model.__tablename__,
                                                                                datum['tableName']))
                    raise errors
            self.table_name = model.__tablename__

        table_name = datum.get('tableName', self.tableName)
        model = self.__class__.model_from_table_name(table_name)
        for (humanized_key, dehumanized_key) in [('oldDatum', 'old_data'), ('patch', 'changed_data')]:
            if humanized_key in dehumanized_datum:
                dehumanized_datum[dehumanized_key] = dehumanize_ids_in(dehumanized_datum[humanized_key],
                                                                       model)
                del dehumanized_datum[humanized_key]

        super().modify(dehumanized_datum,
                       skipped_keys=skipped_keys,
                       with_add=with_add)

    __as_dict_includes__ = [
        'dateCreated',
        'modelName',
        'patch',
        'verb',
        '-changed_data',
        '-issued_at',
        '-native_transaction_id',
        '-old_data',
        '-table_name',
        '-schema_name',
        '-transaction_id'
    ]
