from sqlalchemy import Column, \
                       desc, \
                       Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_api_handler.bases.accessor import Accessor


class ActivityMixin(object):
    __versioned__ = {}

    activityUuid = Column(UUID(as_uuid=True))


    def activities_query(self):
        Activity = Accessor.get_activity()
        is_on_table = Activity.table_name == self.__tablename__
        changed_data_matches_id = Activity.changed_data['id'] \
                                          .astext.cast(Integer) == self.id


    @property
    def activities(self):
        Activity = Accessor.get_activity()
        is_on_table = Activity.table_name == self.__tablename__
        return Activity.query.filter(is_on_table & (Activity.uuid == self.activityUuid)) \
                             .order_by(desc(Activity.id)) \
                             .all()
