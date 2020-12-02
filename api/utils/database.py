from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.utils import logger


db = SQLAlchemy()


def delete():
    logger.info('Delete all the database...')
    for table in reversed(db.metadata.sorted_tables):
        print('Deleting table {table_name}...'.format(table_name=table))
        db.session.execute(table.delete())
    ApiHandler.get_activity().query.delete()
    db.session.commit()
    logger.info('Delete all the database...Done.')


def create_activity_and_transaction_tables():
    orm.configure_mappers()
    Activity = ApiHandler.get_activity()
    #ApiHandler.model_from_name('User').__table__.create(db.session.get_bind())
    Activity.transaction.mapper.class_.__table__.create(db.session.get_bind())
    Activity.__table__.create(db.session.get_bind())


def create():
    logger.info('Create all the database...')
    create_activity_and_transaction_tables()
    '''
    tables_except_user = [
        table
        for (table_name, table) in db.metadata.tables.items()
        if table_name != ApiHandler.model_from_name('User').__tablename__
    ]
    db.metadata.create_all(db.engine,
                           tables=tables_except_user)
    '''
    db.create_all()
    db.session.commit()
    logger.info('Create all the database...Done.')
