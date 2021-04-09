import binascii
from base64 import b32decode
from typing import Any

from sqlalchemy_api_handler.utils.is_id_column import is_id_column


class NonDehumanizableId(Exception):
    pass


def dehumanize(publicId):
    """
    Get back an integer from a human-compatible ID
    This library creates IDs for use in our URLs,
    trying to achieve a balance between having a short
    length and being usable by humans
    We use base32, but replace O and I, which can be mistaken for 0 and 1
    by 8 and 9
    """
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


def int_from_bytes(xbytes):
    return int.from_bytes(xbytes, 'big')


def dehumanize_ids_in(datum, model):
    if datum is None:
        return None
    dehumanized_datum = {**datum}
    for (key, value) in datum.items():
        if hasattr(model, key):
            if is_id_column(getattr(model, key)):
                dehumanized_datum[key] = dehumanize(value)
    return dehumanized_datum


def dehumanize_if_needed(column, value: Any) -> Any:
    if is_id_column(column):
        return dehumanize(value)
    return value
