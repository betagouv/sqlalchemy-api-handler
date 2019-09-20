from sqlalchemy.exc import ProgrammingError
from postgresql_audit.flask import versioning_manager

from tests.test_utils.db import db


def create_versionning_tables():
    # FIXME: This is seriously ugly... (based on https://github.com/kvesteri/postgresql-audit/issues/21)
    try:
        versioning_manager.transaction_cls.__table__.create(db.session.get_bind())
    except ProgrammingError:
        pass
    try:
        versioning_manager.activity_cls.__table__.create(db.session.get_bind())
    except ProgrammingError:
        pass

def create_index_activity_if_not_exists():
    db.engine.execute("CREATE INDEX IF NOT EXISTS idx_activity_objid ON activity(cast(changed_data->>'id' AS INT));")
