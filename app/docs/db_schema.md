# DB Schema — Oguzabat

## Company
- id: int, PK, auto-increment
- name: str, required
- description: text
- logo_url: str
- website: str
- categories: array of str / JSONB

## Project
- id: int, PK
- company_id: int, FK → Company.id
- name: str
- type: str
- opened_date: datetime
- status: enum('Active','Completed','Pending')
- short_description: str
- full_description: text
- gallery: array of str / JSONB

## Partner
- id: int, PK
- name: str
- slogan: str
- logo_url: str
- short_description: str
- tags: array of str / JSONB
- email: str

## News
- id: int, PK
- title: str
- short_description: str
- full_text: text
- image_url: str
- date: datetime

## Vacancy
- id: int, PK
- title: str
- description: text
- location: str
- employment_type: enum('Full-time','Part-time','Internship','Contract')

## Application
- id: int, PK
- vacancy_id: int, FK → Vacancy.id
- name: str
- surname: str
- email: str
- phone: str
- portfolio_url: str
- message: text
- created_at: datetime

## ContactForm
- id: int, PK
- first_name: str
- last_name: str
- email: str
- phone: str
- company_name: str
- message: text
- created_at: datetime

## Связи
- Company → Project (One-to-Many)
- Vacancy → Application (One-to-Many)
- Остальные таблицы без FK

## Валидация
- email: уникальный, валидный формат
- phone: regex
- website: валидный URL
- status: enum
- gallery, categories, tags: массив строк или JSON





слайдер с компаниями, у каждой из которых фото, название, краткое описание, кнопка read more.
hero блок с огузабат, на котором title, description, abuot us, read more
блок с компаниями и их карточки с лого, типом(тег), лого, название, краткое описание.
блок с партнерами, список партнеров у каждого из которых название, лого,  краткое описание, ссылка на партнера.
блок с последними новостями, карточки новостей в каждой из которых лого новости, название, дата, краткое описание, read more 