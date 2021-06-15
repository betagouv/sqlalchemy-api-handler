
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, synonym

from sqlalchemy_api_handler.bases.errors import ActivityError
from sqlalchemy_api_handler.utils.datum import datum_without_synonym_columns_from, \
                                               datum_with_relationships_from, \
                                               datum_with_synonym_columns_from
import sqlalchemy_api_handler.utils.date as date_helper
from sqlalchemy_api_handler.utils.datum import datum_with_dehumanize_ids_from, \
                                               datum_with_humanize_ids_from
from sqlalchemy_api_handler.utils.humanize import humanize



class ActivityMixin(object):

    _entityIdentifier = None

    @declared_attr
    def dateCreated(cls):
        return synonym('issued_at')

    @property
    def entityInsertedAt(self):
        return date_helper.to_datetime(self.data.get('dateCreated')) or self.entity.dateCreated

    @declared_attr
    def tableName(cls):
        return synonym('table_name')

    @property
    def datum(self):
        if self.data is None:
            return None
        model = self.model
        return datum_with_synonym_columns_from(datum_with_humanize_ids_from(self.data, self.model), model)

    @hybrid_property
    def entityIdentifier(self):
        if self._entityIdentifier:
            if isinstance(self._entityIdentifier, str):
                return uuid.UUID(self._entityIdentifier)
            return self._entityIdentifier
        activity_identifier = self.data.get('activityIdentifier')
        if activity_identifier:
            self._entityIdentifier = activity_identifier
            return uuid.UUID(self._entityIdentifier)

    @entityIdentifier.expression
    def entityIdentifier(cls):
        return cls.data['activityIdentifier'].astext.cast(UUID(as_uuid=True))

    @entityIdentifier.setter
    def entityIdentifier(self, value):
        self._entityIdentifier = value

    @property
    def model(self):
        return self.__class__.model_from_table_name(self.table_name)

    @model.setter
    def model(self, value):
        self.table_name = value.__tablename__

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
        activity_identifier = self.entityIdentifier
        if activity_identifier:
            return model.query.filter_by(activityIdentifier=activity_identifier).one()
        return None

    @property
    def oldDatum(self):
        if self.old_data is None:
            return None
        model = self.model
        return datum_with_synonym_columns_from(datum_with_humanize_ids_from(self.old_data, model), model)

    @property
    def patch(self):
        if self.changed_data is None:
            return None
        model = self.model
        return datum_with_synonym_columns_from(datum_with_humanize_ids_from(self.changed_data, model), model)

    @patch.setter
    def patch(self, value):
        model = self.model
        self.changed_data = datum_without_synonym_columns_from(datum_with_dehumanize_ids_from(value, model), model)

    def modify(self, datum, **kwargs):
        if 'modelName' in datum and 'tableName' in datum:
            model = self.__class__.model_from_name(datum['modelName'])
            if datum['tableName'] != model.__tablename__:
                errors = ActivityError()
                errors.add_error('modelName', '{} different from {}'.format(model.__tablename__,
                                                                            datum['tableName']))
                raise errors
        if self.table_name is None:
            table_name = datum.get('tableName')
            if table_name:
                self.table_name = table_name
            else:
                model_name = datum.get('modelName')
                if model_name:
                    self.modelName = datum['modelName']
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
