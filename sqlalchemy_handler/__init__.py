from pprint import pprint
from sqlalchemy import BigInteger,\
                       Column

from sqlalchemy_handler.db import db, Model
from sqlalchemy_handler.find_or_create import FindOrCreate
from sqlalchemy_handler.human_ids import humanize
from sqlalchemy_handler.save import Save

__version__ = "0.0.1"

class Handler(Save, FindOrCreate):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    def dump(self):
        pprint(vars(self))

    def __repr__(self):
        self_id = "unsaved"\
               if self.id is None\
               else str(self.id) + "/" + humanize(self.id)
        return '<%s #%s>' % (self.__class__.__name__, self_id)
