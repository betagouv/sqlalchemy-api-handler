from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


Model = db.Model


def model_from_table_name(table_name):
    for model in Model._decl_class_registry.values():
        if not hasattr(model, '__table__'):
            continue
        if model.__tablename__ == table_name:
            return model


def clean():
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
