from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
from datetime import datetime
from app.models.models import ProjectStatus, EmploymentType
from fastapi import File, UploadFile

# ---------- XReadMin ----------
class ProjectReadMin(BaseModel):
    id: int = Field(..., description="ID проекта", example=1)
    name: str = Field(..., description="Название проекта", example="Smart City B")
    short_description: str = Field(..., description="Краткое описание проекта", example="Urban infrastructure upgrade")
    status: ProjectStatus = Field(..., description="Статус проекта", example=ProjectStatus.Active)

    model_config = ConfigDict(from_attributes=True)


class CompanyReadMin(BaseModel):
    id: int = Field(..., description="ID компании", example=1)
    name: str = Field(..., description="Название компании", example="Oguzabat Tech")
    logo_url: str = Field(..., description="URL логотипа компании", example="/img/oguzabat_tech.png")

    model_config = ConfigDict(from_attributes=True)  


class VacancyReadMinimal(BaseModel):
    id: int = Field(..., description="ID вакансии")
    title: str = Field(..., description="Название вакансии")

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

    class Config:
        orm_mode = True


# ---------- Token ----------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None



# ---------- Projects ----------
class ProjectBase(BaseModel):
    company_id: Optional[int] = Field(None, description="ID компании, которой принадлежит проект", example=1)
    name: Optional[str] = Field(None, description="Название проекта", example="Smart City B")
    type: Optional[str] = Field(None, description="Тип проекта", example="Infrastructure")
    location: Optional[str] = Field(None, description="Местоположение проекта", example="Ashgabat, Turkmenistan")
    opened_date: Optional[datetime] = Field(None, description="Дата начала проекта", example="2025-01-15T00:00:00")
    status: Optional[ProjectStatus] = Field(ProjectStatus.Pending, description="Статус проекта", example=ProjectStatus.Active)
    short_description: Optional[str] = Field(None, description="Краткое описание проекта", example="Urban infrastructure upgrade")
    full_description: Optional[str] = Field(None, description="Полное описание проекта", example="Comprehensive urban development project...")
    gallery: List[str] = Field(default_factory=list, description="Ссылки на изображения проекта", example=["/img/project1.jpg", "/img/project2.jpg"])


class ProjectCreate(ProjectBase):
    company_id: int = Field(..., description="ID компании, которой принадлежит проект", example=1)
    name: str = Field(..., description="Название проекта", example="Smart City B")
    type: str = Field(..., description="Тип проекта", example="Infrastructure")
    opened_date: datetime = Field(..., description="Дата начала проекта", example="2025-01-15T00:00:00")
    short_description: str = Field(..., description="Краткое описание проекта", example="Urban infrastructure upgrade")


class ProjectUpdate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int = Field(..., description="ID проекта", example=1)
    name: str = Field(..., description="Название проекта", example="Smart City B")
    short_description: str = Field(..., description="Краткое описание проекта", example="Urban infrastructure upgrade")
    gallery: List[str] = Field(default_factory=list, description="Ссылки на изображения проекта", example=["/img/project1.jpg", "/img/project2.jpg"])
    company: Optional[CompanyReadMin] = Field(None, description="Информация о компании")

    model_config = ConfigDict(from_attributes=True)


# ---------- News ----------
class NewsRecommendationRead(BaseModel):
    id: int = Field(..., description="ID рекомендованной новости", example=2)
    title: str = Field(..., description="Заголовок рекомендованной новости", example="Related News Title")

    model_config = ConfigDict(from_attributes=True)


class NewsBase(BaseModel):
    title: Optional[str] = Field(None, description="Заголовок новости", example="Новости Oguzabat: Запуск нового проекта")
    short_description: Optional[str] = Field(None, description="Краткое описание новости", example="Компания Oguzabat объявила о запуске нового инфраструктурного проекта...")
    full_text: Optional[str] = Field(None, description="Полный текст новости", example="Подробности о новом проекте...")
    image_url: Optional[str] = Field(None, description="URL изображения новости", example="/img/news_image.jpg")
    date: Optional[datetime] = Field(None, description="Дата публикации новости", example="2025-01-10T12:00:00")


class NewsCreate(NewsBase):
    title: str = Field(..., description="Заголовок новости", example="Новости Oguzabat: Запуск нового проекта")
    short_description: str = Field(..., description="Краткое описание новости", example="Компания Oguzabat объявила о запуске нового инфраструктурного проекта...")
    date: datetime = Field(..., description="Дата публикации новости", example="2025-01-10T12:00:00")


class NewsUpdate(NewsBase):
    pass


class NewsRead(NewsBase):
    id: int = Field(..., description="ID новости", example=1)
    date: datetime = Field(..., description="Дата публикации новости", example="2025-01-10T12:00:00")
    recommendations: List[NewsRecommendationRead] = Field(default_factory=list, description="Рекомендованные новости")

    model_config = ConfigDict(from_attributes=True)


# ---------- Company ----------
class CompanyBase(BaseModel):
    name: Optional[str] = Field(None, description="Название компании", example="Oguzabat Tech")
    description: Optional[str] = Field(None, description="Описание компании", example="Leading tech company in Central Asia")
    logo_url: Optional[str] = Field(None, description="URL логотипа компании", example="/img/oguzabat_tech.png")
    website: Optional[str] = Field(None, description="Сайт компании", example="https://oguzabat.com")
    categories: List[str] = Field(default_factory=list, description="Категории компании", example=["IT", "Engineering"])
    created_at: Optional[datetime] = Field(None, description="Дата создания записи о компании", example="2025-01-01T00:00:00")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления записи", example="2025-01-05T10:00:00")


class CompanyCreate(CompanyBase):
    name: str = Field(..., description="Название компании", example="Oguzabat Tech")
    description: str = Field(..., description="Описание компании", example="Leading tech company in Central Asia")
    logo_url: str = Field(..., description="URL логотипа компании", example="/img/oguzabat_tech.png")
    website: str = Field(..., description="Сайт компании", example="https://oguzabat.com")
    categories: List[str] = Field(default_factory=list, description="Категории компании", example=["IT", "Engineering"])


class CompanyUpdate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    id: int = Field(..., description="ID компании", example=1)
    created_at: datetime = Field(..., description="Дата создания записи о компании", example="2025-01-01T00:00:00")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления записи", example="2025-01-05T10:00:00")
    projects: List[ProjectReadMin] = Field(default_factory=list, description="Проекты компании")

    model_config = ConfigDict(from_attributes=True)

class Message(BaseModel):
    success: bool = Field(..., description="Флаг успешного выполнения операции", example=True)
    message: str = Field(..., description="Сообщение о результате", example="Company deleted successfully")


# ---------- Partner ----------
class PartnerBase(BaseModel):
    name: Optional[str] = Field(None, description="Название партнера", example="Partner A")
    slogan: Optional[str] = Field(None, description="Слоган партнера", example="Building Together")
    logo_url: Optional[str] = Field(None, description="URL логотипа партнера", example="/img/partner_a.png")
    short_description: Optional[str] = Field(None, description="Краткое описание партнера", example="Leading construction partner")
    tags: List[str] = Field(default_factory=list, description="Теги партнера", example=["construction", "infrastructure"])
    email: Optional[str] = Field(None, description="Email партнера", example="contact@partnera.com")


class PartnerCreate(PartnerBase):
    name: str = Field(..., description="Название партнера", example="Partner A")
    slogan: str = Field(..., description="Слоган партнера", example="Building Together")
    logo_url: str = Field(..., description="URL логотипа партнера", example="/img/partner_a.png")
    short_description: str = Field(..., description="Краткое описание партнера", example="Leading construction partner")
    tags: List[str] = Field(default_factory=list, description="Теги партнера", example=["construction", "infrastructure"])
    email: str = Field(..., description="Email партнера", example="contact@partnera.com")


class PartnerUpdate(PartnerBase):
    pass


class PartnerRead(PartnerBase):
    id: int = Field(..., description="ID партнера", example=1)
    name: str = Field(..., description="Название партнера", example="Partner A")
    slogan: str = Field(..., description="Слоган партнера", example="Building Together")
    logo_url: str = Field(..., description="URL логотипа партнера", example="/img/partner_a.png")
    short_description: str = Field(..., description="Краткое описание партнера", example="Leading construction partner")
    tags: List[str] = Field(default_factory=list, description="Теги партнера", example=["construction", "infrastructure"])
    email: str = Field(..., description="Email партнера", example="contact@partnera.com")

    model_config = ConfigDict(from_attributes=True)


# ---------------- Vacancy ----------------
class VacancyBase(BaseModel):
    """
    Базовая схема вакансии. Содержит основные поля, которые наследуются в Create/Update/Read схемах.
    """
    title: Optional[str] = Field(
        None, description="Название вакансии", example="Senior Python Developer"
    )
    description: Optional[str] = Field(
        None, description="Описание вакансии", example="Looking for experienced Python developers..."
    )
    location: Optional[str] = Field(
        None, description="Местоположение", example="Ashgabat, Turkmenistan"
    )
    employment_type: Optional[EmploymentType] = Field(
        EmploymentType.Contract, description="Тип занятости", example=EmploymentType.Full_time
    )


class VacancyCreate(VacancyBase):
    """
    Схема для создания вакансии. Поля title и description обязательны.
    """
    title: str = Field(..., description="Название вакансии", example="Senior Python Developer")
    description: str = Field(..., description="Описание вакансии", example="Looking for experienced Python developers...")


class VacancyUpdate(VacancyBase):
    """
    Схема для обновления вакансии. Все поля опциональные.
    """
    pass


class VacancyRead(VacancyBase):
    """
    Схема для чтения вакансии. Добавляем id и список откликов (applications).
    """
    id: int = Field(..., description="ID вакансии", example=1)
    applications: List["ApplicationRead"] = Field(default_factory=list, description="Список откликов на вакансию")

    model_config = ConfigDict(from_attributes=True)


# ---------------- ApplicationFile ----------------
class ApplicationFileRead(BaseModel):
    """
    Схема для чтения файла отклика.
    """
    id: int = Field(..., description="ID файла приложения", example=1)
    file_url: str = Field(..., description="URL файла", example="uploads/portfolio/1234abcd.pdf")
    created_at: datetime = Field(..., description="Дата загрузки файла", example="2025-10-02T12:30:00")

    model_config = ConfigDict(from_attributes=True)


# ---------------- Application ----------------
class ApplicationBase(BaseModel):
    """
    Базовая схема отклика. Все поля опциональные, наследуются для Create/Update/Read схем.
    """
    vacancy_id: Optional[int] = Field(None, description="ID вакансии, на которую подаётся отклик", example=1)
    name: Optional[str] = Field(None, description="Имя соискателя", example="Иван")
    surname: Optional[str] = Field(None, description="Фамилия соискателя", example="Иванов")
    email: Optional[str] = Field(None, description="Email соискателя", example="ivan@example.com")
    phone_number: Optional[str] = Field(None, description="Номер телефона соискателя", example="+99312345678")
    message: Optional[str] = Field(None, description="Сообщение от соискателя", example="Я очень хочу работать у вас...")
    created_at: Optional[datetime] = Field(None, description="Дата подачи отклика", example="2025-01-10T14:30:00")


class ApplicationCreate(ApplicationBase):
    """
    Схема для создания отклика. Основные поля обязательны.
    """
    vacancy_id: int = Field(..., description="ID вакансии, на которую подаётся отклик", example=1)
    name: str = Field(..., description="Имя соискателя", example="Иван")
    surname: str = Field(..., description="Фамилия соискателя", example="Иванов")
    email: str = Field(..., description="Email соискателя", example="ivan@example.com")
    phone_number: str = Field(..., description="Номер телефона соискателя", example="+99312345678")

class ApplicationUpdate(ApplicationBase):
    """
    Схема для обновления отклика. Все поля опциональные.
    """
    pass


class ApplicationRead(BaseModel):
    id: int = Field(..., description="ID отклика")
    vacancy: Optional[VacancyReadMinimal] = Field(None, description="Вакансия")
    files: List[ApplicationFileRead] = Field(default_factory=list, description="Файлы отклика")
    name: str = Field(..., description="Имя")
    surname: str = Field(..., description="Фамилия")
    email: str = Field(..., description="Email")
    phone_number: str = Field(..., description="Телефон")
    message: Optional[str] = Field(None, description="Сообщение")
    created_at: datetime = Field(..., description="Дата создания")

    model_config = ConfigDict(from_attributes=True)



# ---------- ContactForm ----------
class ContactFormBase(BaseModel):
    first_name: Optional[str] = Field(None, description="Имя отправителя", example="Иван")
    last_name: Optional[str] = Field(None, description="Фамилия отправителя", example="Иванов")
    email: Optional[str] = Field(None, description="Email отправителя", example="ivan@example.com")
    phone_number: Optional[str] = Field(None, description="Номер телефона отправителя", example="+99312345678")
    company_name: Optional[str] = Field(None, description="Название компании отправителя", example="ООО Рога и Копыта")
    message: Optional[str] = Field(None, description="Сообщение", example="Здравствуйте, мы хотим сотрудничать...")
    map_code: Optional[str] = Field(None, description="HTML-код для отображения карты", example="<iframe src='https://www.google.com/maps/embed?...'></iframe>")
    created_at: Optional[datetime] = Field(None, description="Дата отправки формы", example="2025-01-10T15:00:00")


class ContactFormCreate(ContactFormBase):
    first_name: str = Field(..., description="Имя отправителя", example="Иван")
    last_name: str = Field(..., description="Фамилия отправителя", example="Иванов")
    email: str = Field(..., description="Email отправителя", example="ivan@example.com")
    phone_number: str = Field(..., description="Номер телефона отправителя", example="+99312345678")
    company_name: str = Field(..., description="Название компании отправителя", example="ООО Рога и Копыта")
    message: str = Field(..., description="Сообщение", example="Здравствуйте, мы хотим сотрудничать...")


class ContactFormUpdate(ContactFormBase):
    pass 


class ContactFormRead(ContactFormBase):
    id: int = Field(..., description="ID записи формы", example=1)
    first_name: str = Field(..., description="Имя отправителя", example="Иван")
    last_name: str = Field(..., description="Фамилия отправителя", example="Иванов")
    email: str = Field(..., description="Email отправителя", example="ivan@example.com")
    phone_number: str = Field(..., description="Номер телефона отправителя", example="+99312345678")
    company_name: str = Field(..., description="Название компании отправителя", example="ООО Рога и Копыта")
    message: str = Field(..., description="Сообщение", example="Здравствуйте, мы хотим сотрудничать...")
    map_code: Optional[str] = Field(None, description="HTML-код для отображения карты", example="<iframe src='https://www.google.com/maps/embed?...'></iframe>")
    created_at: datetime = Field(..., description="Дата отправки формы", example="2025-01-10T15:00:00")

    model_config = ConfigDict(from_attributes=True)



# ---------- AboutGallery ----------
class AboutGalleryBase(BaseModel):
    image_url: Optional[str] = Field(None, description="Ссылка на изображение галереи", example="image1.jpg")
    order: Optional[int] = Field(None, description="Сортировка")


class AboutGalleryCreate(AboutGalleryBase):
    image_url: str = Field(...,description="Ссылка на изображение галереи", example="image1.jpg")   
    order: int = Field(..., description="Сортировка")

class AboutGalleryUpdate(AboutGalleryBase):
    pass

class AboutGalleryRead(AboutGalleryBase):
    id: int = Field(..., description="ID изображения в галерее", example=1)
    image_url: str = Field(...,description="Ссылка на изображение галереи")
    order: int = Field(..., description="Сортировка")

    model_config = ConfigDict(from_attributes=True)

