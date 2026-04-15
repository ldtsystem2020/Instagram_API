"""TOTP (Time-based One-Time Password) generator.

Compatible with Google Authenticator, Authy, and other TOTP apps.
Implements RFC 6238 (TOTP) with SHA1, 6-digit codes, 30-second interval.
"""
import base64
import hashlib
import hmac
import struct
import time


def generate_totp(secret: str) -> str:
    """Generate a 6-digit TOTP code from a base32 secret key.

    Args:
        secret: Base32-encoded secret key (spaces are stripped automatically).
                Example: "BJ4G MWVY 2KL6 ZSVN TVLA 4DEE MFKV PWOU"

    Returns:
        6-digit TOTP code string (e.g. "173904")
    """
    secret = secret.replace(" ", "").upper()
    # Pad base32 to multiple of 8
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    counter = struct.pack(">Q", int(time.time()) // 30)
    mac = hmac.new(key, counter, hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    code = struct.unpack(">I", mac[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(code % 1000000).zfill(6)
