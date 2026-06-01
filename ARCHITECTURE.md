# ARCHITECTURE

## 1. Архитектурный стиль

Проект - Django monolith с server-rendered frontend.

Ключевые архитектурные правила:
- один Django-проект;
- apps разделены по доменным областям;
- frontend находится в Django templates;
- Bootstrap 5 используется как UI-база;
- бизнес-логика matching вынесена в service layer;
- API-first подход не используется;
- JSON endpoint есть только для карты навыков.

## 1.1. Dependencies and integrations

Dependencies from `requirements.txt`:

| Package | Version constraint | Purpose | Criticality |
| --- | --- | --- | --- |
| `Django` | `>=4.2,<5.0` | Web framework, ORM, auth, templates, admin, migrations | Critical |
| `psycopg2-binary` | `>=2.9` | PostgreSQL database adapter | Critical for PostgreSQL deployments, unused by SQLite fallback |
| `Pillow` | `>=10.0` | Required by Django `ImageField` for avatars/logos | Critical for media upload models |

Python standard library usage:
- `os` for env settings;
- `pathlib.Path` for project paths;
- `dataclasses.dataclass` for matching result;
- `functools.wraps` for permission decorator.

Django contrib apps:
- `admin`
- `auth`
- `contenttypes`
- `sessions`
- `messages`
- `staticfiles`

Middleware stack:

```text
SecurityMiddleware
SessionMiddleware
CommonMiddleware
CsrfViewMiddleware
AuthenticationMiddleware
MessageMiddleware
XFrameOptionsMiddleware
```

External frontend dependencies:
- Bootstrap 5 CDN in templates;
- Bootstrap Icons CDN in templates;
- Chart.js CDN for the skill wheel radar chart;
- Simple Icons CDN for technology logos in skill cards.

No package manager-managed frontend dependencies exist.

Integrations:
- Django Admin only;
- no external auth provider;
- no email provider;
- no payment provider;
- no object storage integration;
- no task queue.

Potentially risky dependencies/config:
- `psycopg2-binary` is convenient for local/demo use; production often prefers building `psycopg2` from system libraries.
- Bootstrap/Chart.js/Simple Icons are loaded from CDN, so UI depends on network availability unless vendored locally.
- `Pillow` handles uploaded images; file validation is still application responsibility.

## 2. Entry points

### Runtime

- `manage.py` - стандартная точка запуска команд Django.
- `config/settings.py` - настройки проекта.
- `config/urls.py` - root URLConf.
- `config/wsgi.py` - WSGI entrypoint.
- `config/asgi.py` - ASGI entrypoint, но realtime/asgi-функции не используются.

### HTTP routes

Основные include в `config/urls.py`:

```text
/admin/                  -> Django Admin
/                        -> apps.core.urls
/register/, /login/      -> apps.users.urls
/profiles/               -> apps.profiles.urls
/skills/                 -> apps.skills.urls
/vacancies/              -> apps.vacancies.urls
/applications/           -> apps.applications.urls
/matching/               -> apps.matching.urls
/api/skill-wheel/        -> apps.matching.views.skill_wheel_api
```

В режиме `DEBUG=True` дополнительно обслуживаются `MEDIA_URL`.

## 3. Слои приложения

```text
Templates
  - HTML
  - Bootstrap classes
  - small vanilla JS

Views
  - request/response
  - auth and role checks
  - form processing
  - redirects/messages

Forms
  - ModelForm validation
  - role-specific UI fields
  - duplicate checks
  - catalog-based skill selection

Services
  - matching algorithm
  - recommendations
  - skill wheel
  - next skills

Models
  - Django ORM entities
  - constraints
  - choices
  - relations

Database
  - SQLite local fallback
  - PostgreSQL if POSTGRES_DB is set
```

## 4. Apps and responsibilities

### `apps.users`

Отвечает за:
- custom user model;
- email-based authentication;
- registration/login views;
- dashboard redirects;
- role-based permission helpers.

Critical files:
- `models.py`
- `managers.py`
- `forms.py`
- `views.py`
- `permissions.py`
- `urls.py`

### `apps.profiles`

Отвечает за:
- student profile;
- employer profile;
- student portfolio projects;
- profile create/edit/detail pages;
- profile settings.

Critical files:
- `models.py`
- `forms.py`
- `views.py`
- `urls.py`

### `apps.skills`

Отвечает за:
- skill catalog;
- student skill CRUD;
- skill level 1..5;
- UI catalog categories/cards.

Critical files:
- `models.py`
- `forms.py`
- `views.py`
- `management/commands/seed_skill_wheel_data.py`

### `apps.vacancies`

Отвечает за:
- public vacancy list/detail;
- employer vacancy CRUD;
- vacancy status management;
- required vacancy skills;
- favorite vacancies.

Critical files:
- `models.py`
- `forms.py`
- `views.py`
- `urls.py`

### `apps.applications`

Отвечает за:
- student applications;
- employer candidate list;
- application status update.

Critical files:
- `models.py`
- `forms.py`
- `views.py`
- `urls.py`

### `apps.matching`

Отвечает за:
- compatibility score;
- recommended vacancies;
- missing skills;
- skill wheel;
- next skill suggestions;
- JSON endpoint for skill wheel.

Critical files:
- `services.py`
- `views.py`
- `urls.py`

### `apps.core`

Отвечает за:
- home page;
- static informational pages;
- demo seed command.

Critical files:
- `views.py`
- `urls.py`
- `management/commands/seed_demo_data.py`

## 5. Frontend architecture

Frontend - Django Templates:

```text
templates/base.html
  -> shared navbar
  -> theme toggle
  -> footer
  -> static CSS includes
  -> Bootstrap CDN

feature templates
  -> forms
  -> cards/tables
  -> role-specific pages
```

CSS разделен на:
- `static/css/app.css` - global layout/theme/shared components;
- `static/css/vacancies_public_list.css` - public vacancy cards;
- `static/css/matching_recommendations.css` - recommendations/skill wheel;
- `static/css/applications_employer.css` - employer candidates.

State management отсутствует. Состояние хранится:
- в Django session/auth;
- в database models;
- в localStorage только для theme mode.

## 6. API structure

Проект не является API-first. Большинство endpoints возвращают HTML.

JSON endpoint:
- `/api/skill-wheel/`
- `/matching/api/skill-wheel/`

Оба вызывают `apps.matching.views.skill_wheel_api`.

## 7. Design patterns used

- Django MTV.
- Service Layer для matching.
- ModelForm-based validation.
- Function-based views.
- Decorator-based permissions.
- `update_or_create`/`get_or_create` для seed commands.
- Database-level unique constraints for duplicate prevention.

## 8. Dependency map

```text
users
  -> profiles through request.user profile lookup

profiles
  -> users.CustomUser

skills
  -> profiles.StudentProfile

vacancies
  -> profiles.EmployerProfile
  -> skills.Skill
  -> applications.Application in views
  -> matching.get_recommended_vacancies in public list/detail

applications
  -> profiles.StudentProfile
  -> vacancies.Vacancy
  -> matching.calculate_vacancy_match in employer candidate views

matching
  -> skills.StudentSkill
  -> vacancies.Vacancy
  -> vacancies.VacancySkill

core
  -> users.CustomUser
  -> profiles.*
  -> vacancies.*
  -> applications.*
  -> matching.get_recommended_vacancies in seed preview
```

## 9. Critical dependency chains

### Recommendations chain

```text
StudentProfile
  -> StudentSkill
  -> Vacancy(status=published)
  -> VacancySkill
  -> matching.services.calculate_vacancy_match()
  -> templates/matching/student_recommendations.html
```

### Employer vacancy creation chain

```text
VacancyForm
  -> StudentSkillForm.SKILL_CATALOG
  -> Skill get_or_create
  -> Vacancy
  -> VacancySkill(weight=1)
```

### Skill wheel chain

```text
StudentSkill.skill.category
  -> matching.SKILL_WHEEL_CATEGORY_SKILLS
  -> compute_skill_wheel()
  -> skill_wheel_api/recommendations page
```

### Candidate match chain

```text
Application
  -> Application.student
  -> Application.vacancy
  -> calculate_vacancy_match()
  -> employer candidate list/detail
```

## 10. Cyclic dependency risks

Нет явных Python import cycles на текущем уровне, но есть плотная связность:
- `vacancies.views` импортирует `applications.models` и `matching.services`;
- `applications.views` импортирует `matching.services` и `vacancies.models`;
- `core.seed_demo_data` импортирует почти все доменные apps.

Не переносить matching logic внутрь `vacancies.models` или `applications.models`: это легко создаст циклические импорты.

## 11. Hidden architecture assumptions

- `request.user.role` всегда один из `student`, `employer`, `admin`.
- Student pages предполагают наличие `StudentProfile`; если его нет, views делают redirect на создание профиля.
- Employer pages предполагают наличие `EmployerProfile`; если его нет, views делают redirect на создание профиля.
- Published vacancies - единственные вакансии, видимые студентам и public pages.
- UI теперь скрывает вес навыка и ставит `weight=1`, но модель и matching-service всё еще поддерживают weighted formula.
- Каталог навыков продублирован между skill forms, vacancy forms и matching skill wheel constants.
