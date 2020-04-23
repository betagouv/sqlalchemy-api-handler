from sqlalchemy_api_handler.bases.accessor import Accessor


class Delete(Accessor):

    @staticmethod
    def delete(*entities):
        db = Accessor.get_db()
        for entity in entities:
             db.session.delete(entity)

        db.session.commit()
