import binascii
from base64 import b32encode, b32decode
from sqlalchemy import BigInteger, Integer
from sqlalchemy.sql.schema import Column
# This library creates IDs for use in our URLs,
# trying to achieve a balance between having a short
# length and being usable by humans
# We use base32, but replace O and I, which can be mistaken for 0 and 1
# by 8 and 9

class NonDehumanizableId(Exception):
    pass


def dehumanize(publicId):
    """ Get back an integer from a human-compatible ID """
    if publicId is None:
        return None
    missing_padding = len(publicId) % 8
    if missing_padding != 0:
        publicId += '=' * (8 - missing_padding)
    try:
        xbytes = b32decode(publicId.replace('8', 'O').replace('9', 'I'))
    except binascii.Error:
        raise NonDehumanizableId('id non dehumanizable')
    return int_from_bytes(xbytes)


def humanize(integer):
    """ Create a human-compatible ID from and integer """
    if integer is None:
        return None
    b32 = b32encode(int_to_bytes(integer))
    return b32.decode('ascii')\
              .replace('O', '8')\
              .replace('I', '9')\
              .rstrip('=')


def int_from_bytes(xbytes):
    return int.from_bytes(xbytes, 'big')


def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def is_id_column(column: Column) -> bool:
    if column is None:
        return False
    return isinstance(column.type, (BigInteger, Integer)) \
           and (column.key.endswith('id') or column.key.endswith('Id'))


def dehumanize_ids_in(datum, model):
    if not datum:
        return None
    dehumanized_datum = {**datum}
    for (key, value) in datum.items():
        if hasattr(model, key):
            if is_id_column(getattr(model, key)):
                dehumanized_datum[key] = dehumanize(value)
    return dehumanized_datum


def humanize_ids_in(datum, model):
    if not datum:
        return None
    humanized_datum = {**datum}
    for (key, value) in datum.items():
        if hasattr(model, key):
            if is_id_column(getattr(model, key)):
                humanized_datum[key] = humanize(value)
    return humanized_datum
