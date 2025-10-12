from pydantic import BaseModel, ConfigDict, EmailStr
from typing import List, Optional
from datetime import datetime, date
from app.models.models import ProjectStatus, EmploymentType


# ---------- XReadMin ----------
class ProjectReadMin(BaseModel):
    id: int
    name: str
    short_description: str
    status: ProjectStatus
    model_config = ConfigDict(from_attributes=True)


class CompanyReadMin(BaseModel):
    id: int
    name: str
    logo_url: str
    model_config = ConfigDict(from_attributes=True)


class VacancyReadMinimal(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


# ---------- User ----------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Token ----------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: Optional[str] = None


# ---------- Projects ----------
class ProjectBase(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None


class ProjectCreate(ProjectBase):
    company_id: int


class ProjectUpdate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int
    company_id: int
    opened_date: date
    created_at: datetime
    updated_at: Optional[datetime] = None
    gallery: List[str] = []
    model_config = ConfigDict(from_attributes=True)


# ---------- News ----------
class NewsRecommendationRead(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


class NewsBase(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    full_text: Optional[str] = None
    image_path: Optional[str] = None


class NewsCreate(NewsBase):
    title: str
    short_description: str
    full_text: str


class NewsUpdate(NewsBase):
    pass


class NewsRead(NewsBase):
    id: int
    date: datetime  # автоматически из БД
    recommendations: List[NewsRecommendationRead] = []
    image_path: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- Company ----------
class CompanyBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    logo_path: Optional[str] = None
    website: Optional[str] = None
    categories: List[str] = []


class CompanyCreate(CompanyBase):
    name: str
    description: str
    logo_path: str
    website: str
    email: str
    categories: List[str] = []


class CompanyUpdate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    id: int
    logo_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    vacancies: List[VacancyRead] = []
    model_config = ConfigDict(from_attributes=True)


# ---------- Partner ----------
class PartnerBase(BaseModel):
    name: Optional[str] = None
    slogan: Optional[str] = None
    logo_path: Optional[str] = None
    short_description: Optional[str] = None
    tags: List[str] = []
    email: Optional[str] = None


class PartnerCreate(PartnerBase):
    name: str
    slogan: str
    logo_path: str
    short_description: str
    email: str


class PartnerUpdate(PartnerBase):
    pass


class PartnerRead(PartnerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- Vacancy ----------
class VacancyBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    logo_path: Optional[str] = None
    employment_type: Optional[EmploymentType] = EmploymentType.Contract



class VacancyCreate(VacancyBase):
    title: str
    description: str


class VacancyUpdate(VacancyBase):
    pass


class VacancyRead(VacancyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    applications: List["ApplicationRead"] = []
    company: Optional[CompanyRead] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- ApplicationFile ----------
class ApplicationFileRead(BaseModel):
    id: int
    file_url: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Application ----------
class ApplicationBase(BaseModel):
    vacancy_id: Optional[int] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    message: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    vacancy_id: int
    name: str
    surname: str
    email: str
    phone_number: str


class ApplicationUpdate(ApplicationBase):
    pass


class ApplicationRead(BaseModel):
    id: int
    vacancy: Optional[VacancyReadMinimal] = None
    files: List[ApplicationFileRead] = []
    name: str
    surname: str
    email: str
    phone_number: str
    message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- ContactForm ----------
class ContactFormBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    message: Optional[str] = None
    map_code: Optional[str] = None

class ContactFormCreate(ContactFormBase):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    company_name: str
    message: str

class ContactFormUpdate(ContactFormBase):
    pass

class ContactFormRead(ContactFormBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- AboutGallery ----------
class AboutUsImageBase(BaseModel):
    image_path: str


class AboutUsImageCreate(AboutUsImageBase):
    pass


class AboutUsImageRead(AboutUsImageBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class AboutUsGalleryBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class AboutUsGalleryCreate(AboutUsGalleryBase):
    images: Optional[List[AboutUsImageCreate]] = []


class AboutUsGalleryUpdate(AboutUsGalleryBase):
    images: Optional[List[AboutUsImageCreate]] = []


class AboutUsGalleryRead(AboutUsGalleryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[AboutUsImageRead] = []

    model_config = ConfigDict(from_attributes=True)


CompanyRead.update_forward_refs()
VacancyRead.update_forward_refs()