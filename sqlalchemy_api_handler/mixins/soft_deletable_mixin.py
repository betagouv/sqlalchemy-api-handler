from sqlalchemy import Column, Boolean


class SoftDeletableMixin():
    isSoftDeleted = Column(Boolean,
                           default=False,
                           nullable=False)
