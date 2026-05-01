"""Kalshi API authentication.

Kalshi requires RSA-PSS SHA256 signatures over (timestamp + method + path)
on every authenticated request. WebSocket auth is the same pattern at
handshake time.

Reference: https://docs.kalshi.com (the official API documentation)
"""

from __future__ import annotations

import base64
import time
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def load_private_key(path: Path) -> rsa.RSAPrivateKey:
    if not path.exists():
        raise FileNotFoundError(
            f"Kalshi private key not found at {path}. "
            "Set KALSHI_PRIVATE_KEY_PATH or place the PEM there."
        )
    data = path.read_bytes()
    key = serialization.load_pem_private_key(data, password=None)
    if not isinstance(key, rsa.RSAPrivateKey):
        raise TypeError("Kalshi key must be an RSA private key in PEM format.")
    return key


def sign_pss(key: rsa.RSAPrivateKey, message: str) -> str:
    sig = key.sign(
        message.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(sig).decode("ascii")


def auth_headers(
    key_id: str, key: rsa.RSAPrivateKey, method: str, path: str
) -> dict[str, str]:
    """Build authenticated headers for a REST or WebSocket request.

    The path is the URL path WITHOUT query parameters. For REST requests
    that include query parameters (e.g. /markets?limit=100), sign only
    /markets. For WebSocket auth at handshake, path is /trade-api/ws/v2.
    """
    ts_ms = str(int(time.time() * 1000))
    msg = ts_ms + method.upper() + path
    signature = sign_pss(key, msg)
    return {
        "KALSHI-ACCESS-KEY": key_id,
        "KALSHI-ACCESS-SIGNATURE": signature,
        "KALSHI-ACCESS-TIMESTAMP": ts_ms,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
