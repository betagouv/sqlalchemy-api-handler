from datetime import datetime, timedelta
from pprint import pformat

from sqlalchemy import BigInteger, \
    CheckConstraint, \
    Column, \
    DateTime, \
    DDL, \
    event, \
    ForeignKey, \
    Integer, \
    Numeric, \
    and_, \
    or_
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql import select, func
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.mixins.soft_deletable_mixin import SoftDeletableMixin

from tests.test_utils.db import Model


class Stock(ApiHandler,
            Model,
            SoftDeletableMixin):
    # We redefine this so we can reference it in the baseScore column_property
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    dateModified = Column(DateTime,
                          nullable=False,
                          default=datetime.utcnow)

    beginningDatetime = Column(DateTime,
                               index=True,
                               nullable=True)

    endDatetime = Column(DateTime,
                         CheckConstraint('"endDatetime" > "beginningDatetime"',
                                         name='check_end_datetime_is_after_beginning_datetime'),
                         nullable=True)

    offerId = Column(BigInteger,
                     ForeignKey('offer.id'),
                     index=True,
                     nullable=False)

    offer = relationship('Offer',
                         foreign_keys=[offerId],
                         backref='stocks')

    price = Column(Numeric(10, 2),
                   CheckConstraint('price >= 0', name='check_price_is_not_negative'),
                   nullable=False)

    available = Column(Integer,
                       index=True,
                       nullable=True)

    groupSize = Column(Integer,
                       nullable=False,
                       default=1)

    bookingLimitDatetime = Column(DateTime,
                                  nullable=True)

    bookingRecapSent = Column(DateTime,
                              nullable=True)

    def errors(self):
        api_errors = super(Stock, self).errors()
        if self.available is not None and self.available < 0:
            api_errors.add_error('available', 'Le stock doit être positif')

        if self.endDatetime \
                and self.beginningDatetime \
                and self.endDatetime <= self.beginningDatetime:
            api_errors.add_error('endDatetime',
                                 'La date de fin de l\'événement doit être postérieure à la date de début')

        return api_errors

    @property
    def isBookable(self):
        return self.bookingLimitDatetime is None \
               or self.bookingLimitDatetime >= datetime.utcnow()

    @property
    def resolvedOffer(self):
        return self.offer or self.eventOccurrence.offer

    @classmethod
    def queryNotSoftDeleted(cls):
        return Stock.query.filter_by(isSoftDeleted=False)
