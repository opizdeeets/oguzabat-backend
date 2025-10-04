API plan - Navigation

GET /navigation
appointment: get list of all pages and available languages
response:
    pages (list of name/url), languages (list of code/name)

---

API plan - Company

GET /companies
appointment: get list of companies
query-parameters(optional):
    tags (list of str) - filter by tags
    limit (int, default = 10)
    offset (int, default = 0)
response: list of companies with fields:
    id, name, logo_url, short_description, tags

GET /companies/{id}
appointment: get detail of company including projects
parameters: id (int)
response:
    id, name, description, logo_url, website, categories
    projects (list of id, name, short_description, status)

POST /companies
appointment: add company (admin)
body requests(JSON):
    name, description, logo_url, website, categories
response: added object with id

PUT /companies/{id}
appointment: edit company
parameters: id (int)
body requests: same as POST

DELETE /companies/{id}
appointment: delete company
parameters: id
response: {"success": true}

---

API plan - Partner

GET /partners
appointment: get list of partners
query-parameters(optional):
    tags (list of str)
    limit (int, default = 10)
    offset (int, default = 0)
response: list of partners with fields:
    id, name, slogan, logo_url, short_description, tags, email

GET /partners/{id}
appointment: get detail of partner
parameters: id (int)
response:
    id, name, slogan, logo_url, short_description, tags, email

POST /partners
appointment: add partner (admin)
body requests(JSON):
    name, slogan, logo_url, short_description, tags, email
response: added object with id

PUT /partners/{id}
appointment: edit partner
parameters: id (int)
body requests: same as POST

DELETE /partners/{id}
appointment: delete partner
parameters: id
response: {"success": true}

---

API plan - News

GET /news
appointment: get news list for main page and card news
query-parameters(optional):
    search(str) - search by title/brief description/full_text
    sort(str, default = date_desc) - sort(date_asc, date_desc)
    limit(int, default = 10)
    offset(int, default = 0)
response: list of news with fields:
    id, title, short_description, image_url, date

GET /news/{id}
appointment: detail of news
parameters: id (int)
response:
    id, title, full_text, image_url, date, recommendations (list of id/title of similar news)

POST /news
appointment: add news (admin)
body requests(JSON):
    title, short_description, full_text, image_url, date
response: added object with id

PUT /news/{id}
appointment: edit news
parameters: id (int)
body requests: same as POST

DELETE /news/{id}
appointment: delete news
parameters: id
response: {"success": true}

---

API plan - Project

GET /projects
appointment: get list of projects
query-parameters(optional):
    limit(int, default = 10)
    offset(int, default = 0)
response: list of projects with fields:
    id, name, short_description, logo_url

GET /projects/{id}
appointment: detail of project
parameters: id (int)
response:
    id, name, type, location, opened_date, status, full_description, gallery (list of urls)

POST /projects
appointment: add project (admin)
body requests(JSON):
    name, type, location, opened_date, status, short_description, full_description, gallery
response: added object with id

PUT /projects/{id}
appointment: edit project
parameters: id (int)
body requests: same as POST

DELETE /projects/{id}
appointment: delete project
parameters: id
response: {"success": true}

---

API plan - Career / Vacancy

GET /vacancies
appointment: get list of vacancies
query-parameters(optional):
    location(str)
    limit(int, default = 10)
    offset(int, default = 0)
response: list of vacancies with fields:
    id, title, description, location, employment_type

GET /vacancies/{id}
appointment: detail of vacancy
parameters: id (int)
response:
    title, description, location, employment_type, what_you_do

POST /vacancies
appointment: add vacancy (admin)
body requests(JSON):
    title, description, location, employment_type, what_you_do
response: added object with id

PUT /vacancies/{id}
appointment: edit vacancy
parameters: id (int)
body requests: same as POST

DELETE /vacancies/{id}
appointment: delete vacancy
parameters: id
response: {"success": true}

---

API plan - Application (Career Form)

POST /vacancies/{id}/apply
appointment: apply for vacancy
parameters: id (int)
body requests(form-data):
    name, surname, email, phone, portfolio(file), message
validation: email valid, phone regex, allowed file types(pdf, docx, jpg, png)
response: {"success": true, "message": "Application submitted"}

---

API plan - ContactForm

POST /contact
appointment: send message to company
body requests(JSON):
    first_name, last_name, email, phone, company_name, message
validation: email valid, phone regex, required fields
response: {"success": true, "message": "Message sent"}
