from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.utils import logger


db = SQLAlchemy()


def delete():
    logger.info('Delete all the database...')
    for table in reversed(db.metadata.sorted_tables):
        print('Deleting table {table_name}...'.format(table_name=table))
        try:
            db.session.execute(table.delete())
        except:
            pass
    db.session.commit()
    logger.info('Delete all the database...Done.')


def create_activity_and_transaction_tables():
    orm.configure_mappers()
    Activity = ApiHandler.get_activity()
    Activity.transaction.mapper.class_.__table__.create(db.session.get_bind())
    Activity.__table__.create(db.session.get_bind())


def create():
    logger.info('Create all the database...')
    create_activity_and_transaction_tables()
    db.create_all()
    db.session.commit()
    logger.info('Create all the database...Done.')
