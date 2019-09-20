from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, desc, ForeignKey, String
from sqlalchemy import and_, ARRAY, Boolean, CheckConstraint, false, Integer, Text, TEXT
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql import select, func
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.utils.date import DateTimes

from tests.test_utils.db import Model
from tests.test_utils.models.product_type import ProductType
from tests.test_utils.models.stock import Stock

class Offer(ApiHandler,
            Model):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    bookingEmail = Column(String(120), nullable=True)

    type = Column(String(50),
                  CheckConstraint("type != 'None'"),
                  index=True,
                  nullable=False)

    name = Column(String(140), nullable=False)

    description = Column(Text, nullable=True)

    conditions = Column(String(120),
                        nullable=True)

    ageMin = Column(Integer,
                    nullable=True)
    ageMax = Column(Integer,
                    nullable=True)

    url = Column(String(255), nullable=True)

    mediaUrls = Column(ARRAY(String(220)),
                       nullable=False,
                       default=[])

    durationMinutes = Column(Integer, nullable=True)

    isNational = Column(Boolean,
                        server_default=false(),
                        default=False,
                        nullable=False)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    @property
    def dateRange(self):
        if ProductType.is_thing(self.type) or not self.notDeletedStocks:
            return DateTimes()

        start = min([stock.beginningDatetime for stock in self.notDeletedStocks])
        end = max([stock.endDatetime for stock in self.notDeletedStocks])
        return DateTimes(start, end)

    @property
    def notDeletedStocks(self):
        return [stock for stock in self.stocks if not stock.isSoftDeleted]
