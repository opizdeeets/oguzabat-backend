from sqladmin import ModelView
from starlette.requests import Request
from sqlalchemy import select

from app.models.models import User

def register_model_view(admin):
    admin.add_view(UserAdmin)


class UserAdmin(ModelView, model=User):
    column_list= [User.id, User.username, User.email, User.is_admin]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.email]
    form_excluded_columns = [User.hashed_password]

    def is_accessible(self, request: Request) -> bool:
        sess = request.session
        return bool(sess.get("is_admin"))

    def is_visible(self, request: Request) -> bool:
        return self.is_accessible(request)  