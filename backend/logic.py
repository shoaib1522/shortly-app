# backend/logic.py

import string

# Define the character set for our short codes (0-9, a-z, A-Z)
BASE62_CHARS = string.digits + string.ascii_letters


def encode_base62(num: int) -> str:
    """
    Encodes a positive integer (like a database ID) into a short Base62 string.
    """
    if num == 0:
        return BASE62_CHARS[0]

    encoded = []
    base = len(BASE62_CHARS)
    while num > 0:
        num, remainder = divmod(num, base)
        encoded.append(BASE62_CHARS[remainder])

    return "".join(reversed(encoded))