from sqlalchemy import orm

from tests.utils.db import db
from tests.utils.activity import create_index_activity_if_not_exists, \
                                 create_versionning_tables

def install_models():

    orm.configure_mappers()

    create_versionning_tables()

    db.create_all()

    create_index_activity_if_not_exists()

    db.session.commit()
