from postgresql_audit.flask import versioning_manager
from sqlalchemy.event import listens_for
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.mixins import ActivityMixin

from api.utils.database import db


versioning_manager.init(db.Model)


class Activity(ActivityMixin,
               ApiHandler,
               versioning_manager.activity_cls):
    __table_args__ = {'extend_existing': True}

    id = versioning_manager.activity_cls.id

ApiHandler.set_activity(Activity)
