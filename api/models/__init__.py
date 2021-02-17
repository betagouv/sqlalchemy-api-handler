# pylint: disable=C0415
# pylint: disable=W0641
# pylint: disable=R0914

from api.utils.database import db


def import_models():
    from api.models.activity import Activity
    from api.models.foo import Foo
    from api.models.offer import Offer
    from api.models.offer_tag import OfferTag
    from api.models.offerer import Offerer
    from api.models.scope import Scope
    from api.models.stock import Stock
    from api.models.tag import Tag
    from api.models.task import Task
    from api.models.time_interval import TimeInterval
    from api.models.user import User
    from api.models.user_offerer import UserOfferer
