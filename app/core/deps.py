from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db  
from app.core.jwt_token import decode_token
from app.services.user_service import get_user_by_username
from app.schemas.schemas import TokenData  
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "COuld not validate credentials",
        headers={"WWW-Authenticaticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(sub=username)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(db, token_data.sub)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user=Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user