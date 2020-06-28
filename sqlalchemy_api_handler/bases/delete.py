from sqlalchemy_api_handler.bases.add import Add


class Delete(Add):

    @staticmethod
    def delete(*entities):
        db = Add.get_db()
        for entity in entities:
             db.session.delete(entity)

        db.session.commit()
