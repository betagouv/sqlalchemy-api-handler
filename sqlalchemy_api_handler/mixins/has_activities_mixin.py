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

    """
    @property
    def __activities__(self):
        Activity = Activator.get_activity()
        query_filter = (Activity.table_name == self.__tablename__) & \
                       (Activity.entityIdentifier == self.activityIdentifier) & \
                       (Activity.verb != None)
        return InstrumentedList(Activity.query.filter(query_filter) \
                                              .order_by(desc(Activity.id)) \
                                              .all())

    @property
    def __insertActivity__(self):
        Activity = Activator.get_activity()
        query_filter = (Activity.table_name == self.__tablename__) & \
                       (Activity.entityIdentifier == self.activityIdentifier) & \
                       (Activity.verb == 'insert')
        return Activity.query.filter(query_filter).one()
    """


    @property
    def __activities__(self):
        Activity = Activator.get_activity()
        query_filter = (Activity.table_name == self.__tablename__) & \
                       (Activity.data['id'].astext.cast(BigInteger) == self.id) & \
                       (Activity.verb != None)
        return InstrumentedList(Activity.query.filter(query_filter) \
                                              #.order_by(desc(Activity.id)) \
                                              .order_by(Activity.dateCreated) \
                                              .all())

    @property
    def __insertActivity__(self):
        Activity = Activator.get_activity()
        query_filter = (Activity.table_name == self.__tablename__) & \
                       (Activity.data['id'].astext.cast(BigInteger) == self.id)  & \
                       (Activity.verb == 'insert')
        return Activity.query.filter(query_filter).one()

    """
    @property
    def __activity_identifiers__(self):

        for relationship in self.__mapper__.relationships:

        #if self.__class__.__name__ != 'Activity' and key.endswith('ActivityIdentifier'):
            relationship_name = key.split('ActivityIdentifier')[0]
            relationship = getattr(self, relationship_name)
            if hasattr(relationship, 'activityIdentifier'):
                return relationship.activityIdentifier
            else:
                return None
    """
