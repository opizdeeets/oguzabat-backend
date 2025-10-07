from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback
from app.routers import company, news, project, about_gallery, partner, contact, application, vacancy
from app.models.models import *
from app.core.db import engine, Base
# from app.core.config import settings
# from app.admin.admin_main import init_admin
# from starlette.middleware.sessions import SessionMiddleware


app = FastAPI( 
    title = "Oguzabat API",
    version = "0.1.0",
    debug = True,
)



@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🔥 ERROR:", "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )


# app.include_router(auth.router)
app.include_router(company.router)
app.include_router(news.router)
app.include_router(project.router)
app.include_router(about_gallery.router)
app.include_router(partner.router)
app.include_router(contact.router)
app.include_router(application.router)
app.include_router(vacancy.router)

