from postgresql_audit.flask import versioning_manager
from sqlalchemy_api_handler import activity_mixin

from tests.test_utils.db import db


versioning_manager.init(db.Model)


class Activity(ApiHandler,
               activity_mixin,
               versioning_manager.activity_cls):

    id = versioning_manager.activity_cls.id
