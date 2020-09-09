from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID
from postgresql_audit.flask import versioning_manager

from utils.db import db


class ActivityMixin(object):
    __versioned__ = {}

    activityUuid = Column(UUID(as_uuid=True),
                          nullable=False)

    def activity(self):
        Activity = versioning_manager.activity_cls
        text_filter = text(
            "table_name='" + self.__tablename__ \
            + "' AND cast(changed_data->>'id' AS INT) = " + str(self.id)
        )
        return Activity.query.filter(text_filter)\
                             .order_by(db.desc(Activity.id))
