from datetime import datetime
import enum
from sqlalchemy import Column, \
                       Boolean, \
                       DateTime, \
                       Enum, \
                       String, \
                       Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func


class TaskState(enum.Enum):
    CREATED = 'created'
    FAILED = 'failed'
    PUBLISHED = 'published'
    RECEIVED = 'received'
    RERUNNED = 'rerunned'
    STARTED = 'started'
    STOPPED = 'stopped'
    SUCCEED = 'succeed'


class TaskMixin(object):

    args = Column(JSON())

    celeryUuid = Column(UUID(as_uuid=True),
                             index=True,
                             nullable=False)

    creationTime = Column(DateTime(),
                          nullable=False,
                          server_default=func.now())

    hostname = Column(String(64))

    isEager = Column(Boolean())

    kwargs = Column(JSON())

    name = Column(String(256),
                  nullable=False)

    queue = Column(String(64))

    planificationTime = Column(DateTime())

    result = Column(JSON())

    state = Column(Enum(TaskState),
                   nullable=False)

    startTime = Column(DateTime())

    stopTime = Column(DateTime())

    traceback = Column(Text())
