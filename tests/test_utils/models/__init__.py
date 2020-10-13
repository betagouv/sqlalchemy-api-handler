# pylint: disable=C0415
# pylint: disable=W0641
# pylint: disable=R0914

from tests.test_utils.database import db


def import_models():
    from tests.test_utils.models.activity import Activity
    from tests.test_utils.models.foo import Foo
    from tests.test_utils.models.offer import Offer
    from tests.test_utils.models.offerer import Offerer
    from tests.test_utils.models.scope import Scope
    from tests.test_utils.models.stock import Stock
    from tests.test_utils.models.tag import Tag
    from tests.test_utils.models.time_interval import TimeInterval
    from tests.test_utils.models.user import User
    from tests.test_utils.models.user_offerer import UserOfferer
