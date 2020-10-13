from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy_api_handler import logger


db = SQLAlchemy()


def delete():
    logger.info('delete all the database...')
    for table in reversed(db.metadata.sorted_tables):
        print('Deleting table {table_name}...'.format(table_name=table))
        db.session.execute(table.delete())
    db.session.commit()
    logger.info('clean all the database...Done.')


def create_activity_and_transaction_and_user_tables():
    # based on https://github.com/kvesteri/postgresql-audit/issues/21
    # plus we need to create user table first as Activity model depends on it
    from tests.test_utils.models.activity import Activity, versioning_manager
    orm.configure_mappers()
    #Activity.user.mapper.class_.__table__.create(db.session.get_bind())
    versioning_manager.transaction_cls.__table__.create(db.session.get_bind())
    Activity.__table__.create(db.session.get_bind())


def create():
    logger.info('create all the database...')
    from tests.test_utils.models.activity import Activity
    create_activity_and_transaction_and_user_tables()
    #tables_except_user = [
    #    table
    #    for (table_name, table) in db.metadata.tables.items()
    #    if table_name != Activity.user.mapper.class_.__tablename__
    #]
    #db.metadata.create_all(db.engine,
    #                       tables=tables_except_user)
    db.create_all()
    db.session.commit()
    logger.info('create all the database...Done.')
