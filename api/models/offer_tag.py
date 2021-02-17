from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy_api_handler import ApiHandler

from api.utils.database import db


class OfferTag(ApiHandler,
               db.Model):

    offerId = Column(BigInteger(),
                       ForeignKey('offer.id'),
                       primary_key=True)

    offer = relationship('Offer',
                         backref=backref('offerTags'),
                         foreign_keys=[offerId])

    tagId = Column(BigInteger(),
                   ForeignKey('tag.id'),
                   primary_key=True)

    tag = relationship('Tag',
                       backref=backref('offerTags'),
                       foreign_keys=[tagId])
