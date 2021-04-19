from datetime import datetime
from uuid import uuid4
from sqlalchemy import BigInteger, \
                       Column, \
                       DateTime, \
                       desc
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_api_handler.bases.activate import Activate
from sqlalchemy_api_handler.bases.errors import IdNoneError, \
                                                JustBeforeActivityNotFound
from sqlalchemy.orm.collections import InstrumentedList




class HasActivitiesMixin(object):
    __versioned__ = {}

    activityIdentifier = Column(UUID(as_uuid=True),
                                     default=uuid4,
                                     index=True)

    dateCreated = Column(DateTime(),
                         default=datetime.utcnow,
                         nullable=False)
                                                       
    def _get_activity_join_by_entity_id_filter(self):
        Activity = Activate.get_activity()
        id_key = self.__class__.id.property.key
        id_value = getattr(self, id_key)
        if id_value is None:
            errors = IdNoneError()
            errors.add_error('_get_activity_join_by_entity_id_filter',
                             f'tried to filter with a None id value for a {self.__class__.__name__} entity')
            raise errors
        return ((Activity.old_data[id_key].astext.cast(BigInteger) == id_value) | \
                (Activity.changed_data[id_key].astext.cast(BigInteger) == id_value))

    def _get_activity_join_filter(self):
        Activity = Activate.get_activity()
        return ((Activity.table_name == self.__tablename__) & \
                (self._get_activity_join_by_entity_id_filter()))

    @property
    def __activities__(self):
        Activity = Activate.get_activity()
        query_filter = self._get_activity_join_filter()
        return InstrumentedList(Activity.query.filter(query_filter) \
                                              .order_by(Activity.dateCreated) \
                                              .order_by(Activity.id) \
                                              .all())

    @property
    def __deleteActivity__(self):
        Activity = Activate.get_activity()
        query_filter = ((self._get_activity_join_filter()) & \
                        (Activity.verb == 'delete'))
        return Activity.query.filter(query_filter).one()

    @property
    def __insertActivity__(self):
        Activity = Activate.get_activity()
        query_filter = (self._get_activity_join_filter()) & \
                       (Activity.verb == 'insert')
        return Activity.query.filter(query_filter).one()

    @property
    def __lastActivity__(self):
        Activity = Activate.get_activity()
        query_filter = (self._get_activity_join_filter()) & \
                       (Activity.verb == 'update')
        return Activity.query.filter(query_filter) \
                             .order_by(desc(Activity.id)) \
                             .limit(1) \
                             .one()


    def just_before_activity_from(self, activity):
        Activity = Activate.get_activity()
        query_filter = (self._get_activity_join_filter()) & \
                       (Activity.dateCreated < activity.dateCreated)

        before_activity = Activity.query.filter(query_filter) \
                                  .order_by(desc(Activity.dateCreated)) \
                                  .first()
        if before_activity is None:
            raise JustBeforeActivityNotFound(f'Failed to find an activity just before that one {vars(activity)}')
        return before_activity
