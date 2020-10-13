from sqlalchemy_api_handler.utils.dehumanize import dehumanize


def load_or_404(obj_class, human_id):
    return obj_class.query.filter_by(id=dehumanize(human_id))\
                          .first_or_404()
