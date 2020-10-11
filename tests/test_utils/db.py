from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy_api_handler.utils.logger import logger


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
    Activity = ApiHandler.model_from_name('activity')
    orm.configure_mappers()
    Activity.user.__class__.__table__.create(db.session.get_bind())
    versioning_manager.transaction_cls.__table__.create(db.session.get_bind())
    Activity.__table__.create(db.session.get_bind())


def create():
    logger.info('create all the database...')
    create_activity_and_transaction_and_user_tables()
    tables_except_user = [
        table
        for (table_name, table) in db.metadata.tables.items()
        if table_name != ApiHandler.model_from_name('activity').user.__tablename__
    ]
    db.metadata.create_all(db.engine,
                           tables=tables_except_user)
    db.session.commit()
    logger.info('create all the database...Done.')
