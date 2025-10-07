from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.core.db import Base
from sqlalchemy.sql import func
import enum
import datetime 

# ---------- User ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)



# ---------- AboutGallery ----------
class AboutGallery(Base):
    __tablename__ = "aboutgallery"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_url = Column(String(255), nullable=False) 
    order = Column(Integer, nullable=False)

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
    date = Column(DateTime, nullable=False)

# ---------- Company ----------
class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    logo_path = Column(String, nullable=False)
    website = Column(String, nullable=False)
    categories = Column(ARRAY(String), nullable=False, default=[])
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    projects = relationship("Project", back_populates="company", cascade="all, delete", lazy="selectin")

# ---------- Project ----------
class ProjectStatus(enum.Enum):
    Active = "Active"
    Completed = "Completed"
    Pending = "Pending"

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("company.id"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    location = Column(String, nullable=True)
    opened_date = Column(DateTime, nullable=False)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.Pending)
    short_description = Column(String, nullable=False)
    full_description = Column(Text)
    gallery = Column(ARRAY(String), nullable=False, default=[])

    company = relationship("Company", back_populates="projects", lazy="joined")

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

    application = relationship("Application", back_populates="vacancy")

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
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    files = relationship("ApplicationFile", back_populates="application")
    vacancy = relationship("Vacancy", back_populates="application")


class ApplicationFile(Base):
    __tablename__ = "application_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("application.id", ondelete="CASCADE"))
    file_url = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

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
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)





