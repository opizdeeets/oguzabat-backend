from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.services.user_service import create_user, authenticate_user, get_user_by_username
from app.core.jwt_token import create_access_token
from app.schemas.schemas import UserCreate, UserRead, Token
from app.core.security import hash_password, verify_password
from app.core.deps import get_current_admin_user, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    try:
        created = await create_user(db, user_in.username, user_in.email, user_in.password)
        return created
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/admin-data")
async def get_admin_data(admin_user=Depends(get_current_admin_user)):
    return {"msg": f"Привет, {admin_user.username}, это админская информация!"}


@router.get("/public-data")
async def get_public_data():
    return {"msg": "Любой может посмотреть"}

