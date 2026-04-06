"""JWT Authentication Service for PolicyAI.

Handles password hashing, JWT token creation/verification,
and provides a FastAPI dependency for protecting routes.
"""

import os
import hashlib
import hmac
import secrets
import json
import time
import base64
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# --- Configuration ---
# In production, set JWT_SECRET as an environment variable
JWT_SECRET = os.environ.get("JWT_SECRET", "policyai_dev_secret_key_change_in_production_2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "72"))

security = HTTPBearer(auto_error=False)


# --- Password Hashing (PBKDF2-SHA256, no external deps) ---

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256 with a random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000
    )
    return f"{salt}:{key.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its PBKDF2-SHA256 hash."""
    try:
        salt, key_hex = hashed.split(':')
        new_key = hashlib.pbkdf2_hmac(
            'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000
        )
        return hmac.compare_digest(new_key.hex(), key_hex)
    except Exception:
        return False


# --- JWT Token Handling (pure Python, no python-jose dependency) ---

def _b64_encode(data: bytes) -> str:
    """URL-safe base64 encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _b64_decode(data: str) -> bytes:
    """URL-safe base64 decode with padding restoration."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)


def create_access_token(user_id: int, email: str, name: str) -> str:
    """Create a JWT access token."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = time.time()
    payload = {
        "sub": str(user_id),
        "email": email,
        "name": name,
        "iat": int(now),
        "exp": int(now + JWT_EXPIRATION_HOURS * 3600),
    }

    header_b64 = _b64_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = _b64_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(JWT_SECRET.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
    sig_b64 = _b64_encode(signature)

    return f"{message}.{sig_b64}"


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token. Returns payload or None."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        message = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(JWT_SECRET.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        actual_sig = _b64_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        # Decode payload
        payload = json.loads(_b64_decode(payload_b64))

        # Check expiration
        if payload.get('exp', 0) < time.time():
            return None

        return payload
    except Exception as e:
        logger.debug(f"Token decode error: {e}")
        return None


# --- FastAPI Dependencies ---

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """FastAPI dependency: extracts and validates the current user from JWT token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": int(payload["sub"]),
        "email": payload["email"],
        "name": payload["name"],
    }


async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """FastAPI dependency: extracts user if token present, else returns None."""
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None:
        return None
    return {
        "id": int(payload["sub"]),
        "email": payload["email"],
        "name": payload["name"],
    }
