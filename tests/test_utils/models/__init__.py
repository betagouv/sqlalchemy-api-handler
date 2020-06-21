# pylint: disable=C0415
# pylint: disable=W0641
# pylint: disable=R0914

from flask_sqlalchemy.model import DefaultMeta
from tests.test_utils.db import db


def import_models():
    from tests.test_utils.models.offer import Offer
    from tests.test_utils.models.offerer import Offerer
    from tests.test_utils.models.stock import Stock
    from tests.test_utils.models.time_interval import TimeInterval
    from tests.test_utils.models.user import User

    db.create_all()
    db.session.commit()


    return [v for v in locals().values() if type(v) == DefaultMeta]
