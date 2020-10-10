import inflect
from sqlalchemy import BigInteger, \
                       Column, \
                       ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, synonym
from sqlalchemy_api_handler import ApiHandler, \
                                   as_dict
from sqlalchemy_api_handler.utils.datum import dehumanize_ids_in, \
                                               humanize_ids_in, \
                                               relationships_in, \
                                               synonyms_in
from postgresql_audit.flask import versioning_manager


inflect_engine = inflect.engine()


class Activity(ApiHandler,
               versioning_manager.activity_cls):
    __table_args__ = {'extend_existing': True}

    dateCreated = synonym('issued_at')

    id = versioning_manager.activity_cls.id

    tableName = synonym('table_name')

    userId = Column(BigInteger(),
                    ForeignKey('user.id'))

    user = relationship('User',
                        foreign_keys=[userId],
                        backref='activities')

    uuid = Column(UUID(as_uuid=True))

    @property
    def collectionName(self):
        return inflect_engine.plural_noun(self.tableName)

    @property
    def datum(self):
        model = ApiHandler.model_from_table_name(self.tableName)
        return relationships_in(synonyms_in(humanize_ids_in(self.data, model), model), model)

    @property
    def object(self):
        model = ApiHandler.model_from_table_name(self.tableName)
        datum_with_humanized_ids = {**self.data}
        for (key, value) in self.data.items():
            if key.endswith('id') or key.endswith('Id'):
                datum_with_humanized_ids[key] = humanize(value)
        return model(**datum_with_humanized_ids)

    @property
    def oldDatum(self):
        model = ApiHandler.model_from_table_name(self.tableName)
        return relationships_in(synonyms_in(humanize_ids_in(self.old_data, model), model), model)

    @property
    def patch(self):
        model = ApiHandler.model_from_table_name(self.tableName)
        return relationships_in(synonyms_in(humanize_ids_in(self.changed_data, model), model), model)

    def modify(self,
               datum,
               skipped_keys=[],
               with_add=False):
        dehumanized_datum = {**datum}

        # if user is set to the instance, it will be automatically added in the session
        # so we need to avoid that
        if 'user' in dehumanized_datum:
            dehumanized_datum['userId'] = humanize(dehumanized_datum['user'].id)
            del dehumanized_datum['user']

        model = ApiHandler.model_from_table_name(datum.get('tableName', self.tableName))
        for (humanized_key, dehumanized_key) in [('oldDatum', 'old_data'), ('patch', 'changed_data')]:
            if humanized_key in dehumanized_datum:
                dehumanized_datum[dehumanized_key] = dehumanize_ids_in(dehumanized_datum[humanized_key],
                                                                       model)
                del dehumanized_datum[humanized_key]
        ApiHandler.modify(self,
                          dehumanized_datum,
                          skipped_keys=skipped_keys,
                          with_add=with_add)


    __as_dict_includes__ = [
        'collectionName',
        'dateCreated',
        'datum',
        'oldDatum',
        'patch',
        'tableName',
        '-changed_data',
        '-issued_at',
        '-native_transaction_id',
        '-old_data',
        '-schema_name',
        '-table_name',
        '-transaction_id',
        '-verb'
    ]
