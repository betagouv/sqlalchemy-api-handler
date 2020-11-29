import inflect
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, synonym

from sqlalchemy_api_handler.bases.errors import ActivityError
from sqlalchemy_api_handler.utils.datum import relationships_in, \
                                               synonyms_in
from sqlalchemy_api_handler.utils.dehumanize import dehumanize_ids_in
from sqlalchemy_api_handler.utils.humanize import humanize, humanize_ids_in


inflect_engine = inflect.engine()


class ActivityMixin(object):
    uuid = Column(UUID(as_uuid=True))

    @declared_attr
    def dateCreated(cls):
        return synonym('issued_at')

    @declared_attr
    def tableName(cls):
        return synonym('table_name')

    @property
    def collectionName(self):
        return inflect_engine.plural_noun(self.tableName)

    @property
    def datum(self):
        if not self.data:
            return None
        model = self.__class__.model_from_table_name(self.tableName)
        return synonyms_in(humanize_ids_in(self.data, model), model)

    @property
    def entity(self):
        model = self.__class__.model_from_table_name(self.tableName)
        return model(**self.datum)

    @property
    def oldDatum(self):
        if not self.old_data:
            return None
        model = self.__class__.model_from_table_name(self.tableName)
        return synonyms_in(humanize_ids_in(self.old_data, model), model)

    @property
    def patch(self):
        if not self.changed_data:
            return None
        model = self.__class__.model_from_table_name(self.tableName)
        return synonyms_in(humanize_ids_in(self.changed_data, model), model)

    def modify(self,
               datum,
               skipped_keys=[],
               with_add=False):
        dehumanized_datum = {**datum}
        table_name = self.tableName

        if 'collectionName' in datum:
            collection_name = datum['collectionName']
            singular_name = inflect_engine.singular_noun(collection_name)

            if table_name:
                if singular_name != table_name:
                    errors = ActivityError()
                    errors.add_error('collectionName',
                                     f'self.tableName {table_name} and passed singular noun from collectionName {singular_name} don\'t match.')
                    raise errors

            if 'tableName' in datum:
                table_name = datum['tableName']
                if singular_name != table_name:
                    errors = ActivityError()
                    errors.add_error('collectionName',
                                     f'Passed tableName {table_name} and singular noun from collectionName {singular_name} don\'t match.')
                    raise errors
            else:
                dehumanized_datum['tableName'] = singular_name
                table_name = singular_name

        model = self.__class__.model_from_table_name(datum.get('tableName', table_name))
        for (humanized_key, dehumanized_key) in [('oldDatum', 'old_data'), ('patch', 'changed_data')]:
            if humanized_key in dehumanized_datum:
                dehumanized_datum[dehumanized_key] = dehumanize_ids_in(dehumanized_datum[humanized_key],
                                                                       model)
                del dehumanized_datum[humanized_key]

        super().modify(dehumanized_datum,
                       skipped_keys=skipped_keys,
                       with_add=with_add)

    __as_dict_includes__ = [
        'collectionName',
        'dateCreated',
        'patch',
        'tableName',
        '-changed_data',
        '-issued_at',
        '-native_transaction_id',
        '-old_data',
        '-table_name',
        '-schema_name',
        '-transaction_id',
        '-verb'
    ]
