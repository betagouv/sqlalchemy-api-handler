import uuid
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, synonym

from sqlalchemy_api_handler.bases.errors import ActivityError
from sqlalchemy_api_handler.utils.datum import relationships_in, \
                                               synonyms_in
from sqlalchemy_api_handler.utils.dehumanize import dehumanize_ids_in
from sqlalchemy_api_handler.utils.humanize import humanize, humanize_ids_in


class ActivityMixin(object):
    _entityIdentifier = None

    @declared_attr
    def dateCreated(cls):
        return synonym('issued_at')

    @declared_attr
    def tableName(cls):
        return synonym('table_name')

    @property
    def datum(self):
        if self.data is None:
            return None
        model = self.model
        return synonyms_in(humanize_ids_in(self.data, self.model), model)

    @property
    def entityIdentifier(self):
        if self._entityIdentifier:
            return self._entityIdentifier
        activity_identifier = self.data.get('activityIdentifier',
                                            self.changed_data.get('activityIdentifier'))
        if activity_identifier:
            self._entityIdentifier = uuid.UUID(activity_identifier)
            return self._entityIdentifier

    @entityIdentifier.setter
    def entityIdentifier(self, value):
        self._entityIdentifier = value

    @property
    def model(self):
        return self.__class__.model_from_table_name(self.table_name)

    @model.setter
    def model(self, value):
        self.table_name = value.__tablename__
        return self.model

    @property
    def modelName(self):
        return self.model.__name__

    @modelName.setter
    def modelName(self, value):
        model = self.__class__.model_from_name(value)
        self.table_name = model.__tablename__

    @property
    def entity(self):
        model = self.model
        return model(**self.datum)

    @property
    def oldDatum(self):
        if self.old_data is None:
            return None
        model = self.model
        return synonyms_in(humanize_ids_in(self.old_data, model), model)

    @property
    def patch(self):
        if self.changed_data is None:
            return None
        model = self.model
        return synonyms_in(humanize_ids_in(self.changed_data, model), model)

    @patch.setter
    def patch(self, value):
        model = self.model
        self.changed_data = dehumanize_ids_in(value, model)


    def modify(self, datum, **kwargs):
        if 'modelName' in datum and 'tableName' in datum:
            model = self.__class__.model_from_name(datum['modelName'])
            if datum['tableName'] != model.__tablename__:
                errors = ActivityError()
                errors.add_error('modelName', '{} different from {}'.format(model.__tablename__,
                                                                            datum['tableName']))
                raise errors

        super().modify(datum, **kwargs)

    __as_dict_includes__ = [
        'dateCreated',
        'entityIdentifier',
        'modelName',
        'patch',
        'verb',
        '-changed_data',
        '-issued_at',
        '-native_transaction_id',
        '-old_data',
        '-table_name',
        '-relid',
        '-schema_name',
        '-transaction_id'
    ]
