from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, func,
    ForeignKey, Enum as SQLEnum, Boolean
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from app.core.db import Base
import enum


# ---------- User ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# ---------- AboutGallery ----------
class AboutUsGallery(Base):
    __tablename__ = "about_us_gallery"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True, default="About Us Gallery")
    description = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # связь с изображениями
    images = relationship("AboutUsImage", back_populates="gallery", cascade="all, delete-orphan", lazy="selectin")


class AboutUsImage(Base):
    __tablename__ = "about_us_images"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)

    gallery_id = Column(Integer, ForeignKey("about_us_gallery.id", ondelete="CASCADE"))

    gallery = relationship("AboutUsGallery", back_populates="images")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ---------- Enum для сортировки ----------
from enum import Enum
class SortOrder(str, Enum):
    order_asc = "order_asc"
    order_desc = "order_desc"


# ---------- News ----------
class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    short_description = Column(String)
    full_text = Column(Text)
    image_path = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# ---------- Company ----------
class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    logo_path = Column(String, nullable=True)
    website = Column(String, nullable=False)
    categories = Column(ARRAY(String), nullable=False, server_default="{}")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    projects = relationship("Project", back_populates="company", cascade="all, delete", lazy="selectin")
    vacancies = relationship("Vacancy", back_populates="company", cascade="all, delete", lazy="selectin")

# ---------- Project ----------
class ProjectStatus(enum.Enum):
    Active = "Active"
    Completed = "Completed"
    Pending = "Pending"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)

    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    location = Column(String, nullable=True)

    opened_date = Column(Date, nullable=False, server_default=func.current_date())
    status = Column(String, default="Pending", nullable=False)
    short_description = Column(String, nullable=True)
    full_description = Column(String, nullable=True)
    gallery = Column(JSONB, nullable=False, server_default="[]")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="projects")


# ---------- Partner ----------
class Partner(Base):
    __tablename__ = "partner"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    slogan = Column(String, nullable=False)
    logo_path = Column(String, nullable=False)
    short_description = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=False, default=[])
    email = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ---------- Vacancy ----------
class EmploymentType(enum.Enum):
    Full_time = "Full time"
    Part_time = "Part time"
    Internship = "Internship"
    Contract = "Contract"


class Vacancy(Base):
    __tablename__ = "vacancy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=True)
    employment_type = Column(SQLEnum(EmploymentType), nullable=False, default=EmploymentType.Contract)
    logo_path = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    application = relationship("Application", back_populates="vacancy")

    company_id = Column(Integer, ForeignKey("company.id", ondelete="SET NULL"), nullable=True)
    company = relationship("Company", back_populates="vacancies", lazy="selectin")

# ---------- Application ----------
class Application(Base):
    __tablename__ = "application"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vacancy_id = Column(Integer, ForeignKey("vacancy.id"))
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    message = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    files = relationship("ApplicationFile", back_populates="application")
    vacancy = relationship("Vacancy", back_populates="application")


# ---------- ApplicationFile ----------
class ApplicationFile(Base):
    __tablename__ = "application_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("application.id", ondelete="CASCADE"))
    file_url = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    application = relationship("Application", back_populates="files")


# ---------- ContactForm ----------
class ContactForm(Base):
    __tablename__ = "contact_form"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    map_code = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), default=func.now())
