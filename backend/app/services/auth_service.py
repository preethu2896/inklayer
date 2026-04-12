from datetime import datetime, timedelta
from typing import Optional
import os

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# ── Config from environment ─────────────────────────────────────────────
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change_me_in_production")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_please_change")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# ── Password Hashing ────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")


def verify_admin_credentials(username: str, password: str) -> bool:
    """
    Validates admin credentials against environment-configured values.
    In production, use a hashed password stored securely.
    """
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT token with an expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    """
    FastAPI dependency — validates JWT and returns admin username.
    Raises 401 if the token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
