from pprint import pprint
from sqlalchemy import BigInteger,\
                       Column

from sqlalchemy_api_handler.bases.activator import Activator
from sqlalchemy_api_handler.utils.human_ids import humanize


class ApiHandler(Activator):

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
