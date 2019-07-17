from flask_sqlalchemy import SQLAlchemy
from postgresql_audit.flask import versioning_manager

db = SQLAlchemy()

Model = db.Model

versioning_manager.init(Model)

def get_model_with_table_name(table_name):
    for model in Model._decl_class_registry.values():
        if not hasattr(model, '__table__'):
            continue
        if model.__tablename__ == table_name:
            return model
