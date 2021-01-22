import os
from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.utils import logger

from api.utils.config import APP_NAME


LOCALHOST_POSTGRES_URL = f'postgresql://{APP_NAME}_user:{APP_NAME}_password@apipostgresdb/{APP_NAME}_apipostgres'
POSTGRES_URL = os.environ.get('POSTGRES_URL', LOCALHOST_POSTGRES_URL)

db = SQLAlchemy()
ApiHandler.set_db(db)


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
    Activity.transaction.mapper.class_.__table__.create(db.session.get_bind())
    Activity.__table__.create(db.session.get_bind())


def create():
    logger.info('Create all the database...')
    create_activity_and_transaction_tables()
    db.create_all()
    db.session.commit()
    logger.info('Create all the database...Done.')
