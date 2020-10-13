from sqlalchemy import BigInteger, Integer
from sqlalchemy.sql.schema import Column


def is_id_column(column: Column) -> bool:
    if column is None:
        return False
    return isinstance(column.type, (BigInteger, Integer)) \
           and (column.key.endswith('id') or column.key.endswith('Id'))
