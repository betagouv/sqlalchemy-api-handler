from sqlalchemy import Column, \
                       desc
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_api_handler.bases.activator import Activator
from sqlalchemy.orm.collections import InstrumentedList


class HasActivitiesMixin(object):
    __versioned__ = {}

    activityUuid = Column(UUID(as_uuid=True))

    @property
    def activities(self):
        Activity = Activator.get_activity()
        query_filter = (Activity.table_name == self.__tablename__) & \
                       (Activity.uuid == self.activityUuid)
        return InstrumentedList(Activity.query.filter(query_filter) \
                                              .order_by(desc(Activity.id)) \
                                              .all())
