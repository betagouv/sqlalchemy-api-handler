from base64 import b32encode

# This library creates IDs for use in our URLs,
# trying to achieve a balance between having a short
# length and being usable by humans
# We use base32, but replace O and I, which can be mistaken for 0 and 1
# by 8 and 9


def humanize(integer):
    """ Create a human-compatible ID from and integer """
    if integer is None:
        return None
    b32 = b32encode(int_to_bytes(integer))
    return b32.decode('ascii')\
              .replace('O', '8')\
              .replace('I', '9')\
              .rstrip('=')


def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')
