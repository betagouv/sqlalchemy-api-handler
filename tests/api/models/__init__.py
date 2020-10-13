# pylint: disable=C0415
# pylint: disable=W0641
# pylint: disable=R0914

from tests.api.database import db


def import_models():
    from tests.api.models.activity import Activity
    from tests.api.models.foo import Foo
    from tests.api.models.offer import Offer
    from tests.api.models.offerer import Offerer
    from tests.api.models.scope import Scope
    from tests.api.models.stock import Stock
    from tests.api.models.tag import Tag
    from tests.api.models.time_interval import TimeInterval
    from tests.api.models.user import User
    from tests.api.models.user_offerer import UserOfferer
