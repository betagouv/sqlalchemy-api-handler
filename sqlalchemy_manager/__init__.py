from pprint import pprint
from sqlalchemy import BigInteger,\
                       Column

from find_or_create import FindOrCreate
from human_ids import humanize
from save import Save


class Manager(Save, FindOrCreate):
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
