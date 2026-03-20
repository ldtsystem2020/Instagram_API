"""Instagram password encryption (#PWD_INSTAGRAM format)."""
import os
import struct
import time
import base64

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


def encrypt_password(password: str, key_id: int, public_key_pem: str) -> str:
    """Encrypt password into #PWD_INSTAGRAM:4:<ts>:<payload> format.

    Args:
        password: Plain text password
        key_id: Encryption key ID from server
        public_key_pem: RSA public key in PEM format

    Returns:
        Encrypted password string like #PWD_INSTAGRAM:4:1234567890:base64data
    """
    timestamp = int(time.time())

    # Generate random 32-byte AES key and 12-byte IV
    aes_key = os.urandom(32)
    iv = os.urandom(12)

    # Encrypt password with AES-256-GCM
    # AAD (additional authenticated data) = timestamp as string
    aad = str(timestamp).encode()
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
    cipher.update(aad)
    ciphertext, tag = cipher.encrypt_and_digest(password.encode())

    # Encrypt AES key with RSA
    rsa_key = RSA.import_key(public_key_pem)
    rsa_cipher = PKCS1_v1_5.new(rsa_key)
    encrypted_aes_key = rsa_cipher.encrypt(aes_key)

    # Build binary payload:
    #   1 byte:  version (1)
    #   1 byte:  key_id
    #   12 bytes: IV
    #   2 bytes: encrypted AES key length (little-endian)
    #   N bytes: RSA-encrypted AES key
    #   16 bytes: AES-GCM tag
    #   M bytes: AES-GCM ciphertext
    payload = b"".join([
        b"\x01",                                        # version
        struct.pack("<B", key_id),                       # key_id
        iv,                                              # 12 bytes
        struct.pack("<H", len(encrypted_aes_key)),       # encrypted key length
        encrypted_aes_key,                               # RSA-encrypted AES key
        tag,                                             # 16 bytes GCM tag
        ciphertext,                                      # encrypted password
    ])

    encoded = base64.b64encode(payload).decode()
    return f"#PWD_INSTAGRAM:4:{timestamp}:{encoded}"
