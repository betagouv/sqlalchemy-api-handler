import inflect
from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, synonym

from sqlalchemy_api_handler.serialization.as_dict import as_dict
from sqlalchemy_api_handler.utils.datum import dehumanize_ids_in, \
                                               humanize_ids_in, \
                                               relationships_in, \
                                               synonyms_in



inflect_engine = inflect.engine()


class ActivityMixin(object):
    @declared_attr
    def dateCreated(cls):
        return synonym('issued_at')

    @declared_attr
    def tableName(cls):
        return synonym('table_name')


    @declared_attr
    def userId(cls):
        return Column(BigInteger(),
                      ForeignKey('user.user_id'))

    @declared_attr
    def user(cls):
        return relationship('User',
                            backref='activities',
                            foreign_keys=[userId])

    uuid = Column(UUID(as_uuid=True))

    @property
    def collectionName(self):
        return inflect_engine.plural_noun(self.tableName)

    @property
    def datum(self):
        model = self.__class__.model_from_table_name(self.tableName)
        return relationships_in(synonyms_in(humanize_ids_in(self.data, model), model), model)

    @property
    def object(self):
        model = self.__class__.model_from_table_name(self.tableName)
        datum_with_humanized_ids = {**self.data}
        for (key, value) in self.data.items():
            if key.endswith('id') or key.endswith('Id'):
                datum_with_humanized_ids[key] = humanize(value)
        return model(**datum_with_humanized_ids)

    @property
    def oldDatum(self):
        model = self.__class__.model_from_table_name(self.tableName)
        return relationships_in(synonyms_in(humanize_ids_in(self.old_data, model), model), model)

    @property
    def patch(self):
        model = self.__class__.model_from_table_name(self.tableName)
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

        model = self.__class__.model_from_table_name(datum.get('tableName', self.tableName))
        for (humanized_key, dehumanized_key) in [('oldDatum', 'old_data'), ('patch', 'changed_data')]:
            if humanized_key in dehumanized_datum:
                dehumanized_datum[dehumanized_key] = dehumanize_ids_in(dehumanized_datum[humanized_key],
                                                                       model)
                del dehumanized_datum[humanized_key]
        self.__class__.modify(self,
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
