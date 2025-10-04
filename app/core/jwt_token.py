from datetime import datetime, timedelta
from jose import jwt
from typing import Optional, Dict, Any

from app.core.config import settings

# SECRET_KEY = "super_secret_key"  
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode: Dict[str, Any] = {}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"sub": str(subject), "exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload




