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
    _entityIdentifier = Column(UUID(as_uuid=True),
                               index=True)

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

    """
    @property
    def entityIdentifier(self):
        activity_identifier = self.data.get('activityIdentifier',
                                            self.changed_data.get('activityIdentifier'))
        if activity_identifier:
            return uuid.UUID(activity_identifier).hex

    @entityIdentifier.setter
    def entityIdentifier(self, value):
        self.changed_data = {
            **(self.changed_data or {}),
            'activityIdentifier': value
        }
    """


    @hybrid_property
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
        self.changed_data = {
            **(self.changed_data or {}),
            'activityIdentifier': str(value)
        }
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
        #dehumanized_datum = {**datum}

        if 'modelName' in datum and 'tableName' in datum:
            model = self.__class__.model_from_name(datum['modelName'])
            if datum['tableName'] != model.__tablename__:
                errors = ActivityError()
                errors.add_error('modelName', '{} different from {}'.format(model.__tablename__,
                                                                            datum['tableName']))
                raise errors

        """
        if 'tableName' in datum:
            self.table_name = datum['tableName']
            del dehumanized_datum['tableName']
        elif 'modelName' in datum:
            self.modelName = datum['modelName']
            del dehumanized_datum['modelName']


        #table_name = datum.get('tableName', self.tableName)
        model = self.__class__.model_from_table_name(self.table_name)
        for (humanized_key, dehumanized_key) in [('oldDatum', 'old_data'), ('patch', 'changed_data')]:
            if humanized_key in dehumanized_datum:
                dehumanized_datum[dehumanized_key] = dehumanize_ids_in(dehumanized_datum[humanized_key],
                                                                       model)
                del dehumanized_datum[humanized_key]
        """

        """
        super().modify(dehumanized_datum,
                       skipped_keys=skipped_keys,
                       with_add=with_add)
        """
        super().modify(datum, **kwargs)

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
        '-relid',
        '-schema_name',
        '-transaction_id'
    ]
