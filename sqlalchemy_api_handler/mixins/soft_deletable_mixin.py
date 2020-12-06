from sqlalchemy import Column, Boolean


class SoftDeletableMixin(object):
    isSoftDeleted = Column(Boolean,
                           default=False,
                           nullable=False)
