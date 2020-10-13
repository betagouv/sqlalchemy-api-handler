from sqlalchemy import BigInteger, \
                       Column, \
                       DateTime, \
                       Float, \
                       Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import synonym
from sqlalchemy_api_handler import ApiHandler

from tests.test_utils.database import db


class Foo(ApiHandler,
          db.Model):
    date_attribute = Column(DateTime(), nullable=True)

    entityId = Column(BigInteger(), nullable=True)

    float_attribute = Column(Float(), nullable=True)

    integer_attribute = Column(Integer(), nullable=True)

    uuid_attribute = Column(UUID(as_uuid=True), nullable=True)

    uuidId = Column(UUID(as_uuid=True), nullable=True)

    bar_id = Column(BigInteger())

    barId = synonym('bar_id')
