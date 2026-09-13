"""
Password hashing and JWT token helpers.

Password hashing uses the `bcrypt` library directly (NOT passlib's
CryptContext). passlib==1.7.4's bcrypt backend probes for a
`bcrypt.__about__.__version__` attribute to detect the installed bcrypt
version; bcrypt>=4.1 removed that attribute, which makes every hash/verify
call raise:
    AttributeError: module 'bcrypt' has no attribute '__about__'
Calling bcrypt's hashpw/checkpw ourselves avoids that version-probe code
path entirely, so this works with any current bcrypt release.
"""
import os
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "resqai-dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# bcrypt only uses the first 72 bytes of a password and raises on longer
# input in recent versions, so truncate defensively before hashing/checking.
_BCRYPT_MAX_BYTES = 72


def _prepare(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(_prepare(password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_prepare(plain_password), hashed_password.encode("utf-8"))
    except ValueError:
        # Malformed/unrecognized hash (e.g. leftover passlib-format hash from
        # an older DB) - treat as a failed login rather than crashing.
        return False


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        return None
