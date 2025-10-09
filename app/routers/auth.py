from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.services.user_service import create_user, get_user_by_username
from app.core.jwt_token import create_access_token
from app.schemas.schemas import UserRead, Token
from app.core.security import verify_password
from app.core.deps import get_current_admin_user

router = APIRouter(prefix="/auth", tags=["auth"])

# ------------------- REGISTER -------------------

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя (через форму)"
)
async def register(
    username: str = Form(..., description="Уникальное имя пользователя"),
    email: str = Form(..., description="Адрес электронной почты"),
    password: str = Form(..., description="Пароль"),
    db: AsyncSession = Depends(get_db),
):
    """
    Регистрирует нового пользователя через **форму** в Swagger.

    **Введите:**
    - `username` — имя пользователя
    - `email` — адрес электронной почты
    - `password` — пароль
    """
    existing = await get_user_by_username(db, username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    try:
        created = await create_user(db, username, email, password)
        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ------------------- LOGIN -------------------

@router.post(
    "/token",
    response_model=Token,
    summary="Авторизация и получение токена (через форму)"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Авторизация пользователя через **форму** (удобный ввод полей в Swagger).

    **Введите:**
    - `username` — имя пользователя
    - `password` — пароль

    Возвращает:
    - `access_token` — JWT токен
    - `token_type` — тип токена (`bearer`)
    """
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------- ADMIN DATA -------------------

@router.get(
    "/admin-data",
    summary="Доступно только администратору",
)
async def get_admin_data(admin_user=Depends(get_current_admin_user)):
    """
    Эндпоинт, доступный только пользователю с ролью администратора.
    """
    return {"msg": f"Привет, {admin_user.username}, это админская информация!"}


# ------------------- PUBLIC DATA -------------------

@router.get(
    "/public-data",
    summary="Открытый эндпоинт"
)
async def get_public_data():
    """
    Эндпоинт, доступный всем пользователям без авторизации.
    """
    return {"msg": "Любой может посмотреть"}
