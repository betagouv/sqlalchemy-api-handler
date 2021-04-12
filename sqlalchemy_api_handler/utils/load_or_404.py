# pylint: disable=C0301

from sqlalchemy_api_handler.utils.dehumanize import dehumanize
from sqlalchemy_api_handler.utils.humanize import humanize
from werkzeug.exceptions import NotFound


class WrongHumanizeId(Exception):
    pass


def load_or_404(obj_class, human_id):
    dehumanized_id = dehumanize(human_id)
    base_human_id = humanize(dehumanized_id)
    if base_human_id != human_id:
        raise NotFound('this humanized id {} is not the correct base value for the matching dehumanized id {}, it should be {}'.format(human_id, dehumanized_id, base_human_id))

    return obj_class.query.filter_by(id=dehumanized_id)\
                          .first_or_404()
