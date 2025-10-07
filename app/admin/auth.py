# from sqladmin.authentication import AuthenticationBackend
# from starlette.requests import Request
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from starlette.responses import RedirectResponse
#
# # импорт ваших утилит/моделей/сенситов
# from app.models.models import User
# from app.core.security import verify_password
# from app.core.jwt_token import decode_token
# from app.core.db import AsyncSessionLocal as async_session  # sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
# from app.core.config import settings
# from app.services.user_service import get_user_by_username
#
#
# class AdminAuth(AuthenticationBackend):
#     def __init__(self):
#         super().__init__(secret_key=settings.SECRET_KEY)
#
#     async def login(self, request: Request) -> bool:
#         form = await request.form()
#         username = form.get("username")
#         password = form.get("password")
#
#         async with async_session() as session:
#             user = await get_user_by_username(session, username)
#
#         if not username or not user.is_admin:
#             return False
#
#         request.session.update({"username": user.username})
#         return True
#
#
#     async def logout(self, request: Request) -> bool:
#         request.session.clear()
#         return True
#
#     async def authenticate(self, request: Request):
#         username = request.session.get("username")
#
#         if not username:
#             return RedirectResponse(request.url_for("admin:login"), status_code=302)
#
#         async with async_session() as session:
#             user = await get_user_by_username(session, username)
#             if not user or not user.is_admin:
#                 return RedirectResponse(request.url_for("admin:login"), status_code=302)
#
#         return True