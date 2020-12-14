from uuid import uuid4
from sqlalchemy import BigInteger, \
                       Column, \
                       desc
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_api_handler.bases.activator import Activator
from sqlalchemy.orm.collections import InstrumentedList


class HasActivitiesMixin(object):
    __versioned__ = {}

    activityIdentifier = Column(UUID(as_uuid=True),
                                     default=uuid4,
                                     index=True)

    def _get_activity_join_by_entity_id_filter(self):
        Activity = Activator.get_activity()
        id_key = self.__class__.id.property.key
        id_value = getattr(self, id_key)
        return (
            (Activity.old_data[id_key].astext.cast(BigInteger) == id_value) | \
            (Activity.changed_data[id_key].astext.cast(BigInteger) == id_value)
        )

    def _get_activity_join_filter(self):
        Activity = Activator.get_activity()
        return (
            (Activity.table_name == self.__tablename__) & \
            (self._get_activity_join_by_entity_id_filter())
        )

    @property
    def __activities__(self):
        Activity = Activator.get_activity()
        query_filter = self._get_activity_join_filter()
        return InstrumentedList(Activity.query.filter(query_filter) \
                                              .order_by(Activity.dateCreated) \
                                              .order_by(Activity.id) \
                                              .all())

    @property
    def __deleteActivity__(self):
        Activity = Activator.get_activity()
        query_filter = (
            (self._get_activity_join_filter()) & \
            (Activity.verb == 'delete')
        )
        return Activity.query.filter(query_filter).one()

    @property
    def __insertActivity__(self):
        Activity = Activator.get_activity()
        query_filter = (self._get_activity_join_filter()) & \
                       (Activity.verb == 'insert')
        return Activity.query.filter(query_filter).one()

    @property
    def __lastActivity__(self):
        Activity = Activator.get_activity()
        query_filter = (self._get_activity_join_filter()) & \
                       (Activity.verb == 'update')
        return Activity.query.filter(query_filter) \
                             .order_by(desc(Activity.dateCreated)) \
                             .limit(1) \
                             .one()
