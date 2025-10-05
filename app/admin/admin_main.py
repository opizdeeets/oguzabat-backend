from typing import Optional

from fastapi import FastAPI
from sqladmin import Admin

from app.admin.views import register_model_view  # функция, регистрирующая все ModelView
from app.admin.auth import AdminAuth
from app.core.db import engine as db




def init_admin(app: FastAPI, engine) -> Admin:
    auth_backend = AdminAuth()
    admin = Admin(app=app, engine=db, authentication_backend=auth_backend)
    register_model_view(admin)
    return admin

