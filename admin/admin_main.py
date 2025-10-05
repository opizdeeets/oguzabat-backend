from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Model
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.models.models import User 
from 



admin_app = admin_app(
    title="Admin Panel",
    login_provider=UsernamePasswordProvider(
        admin_model=User,  # сюда подставляем вашу модель User
        login_field="username",
        password_field="hashed_password",
        session=get_db()
    )
)

