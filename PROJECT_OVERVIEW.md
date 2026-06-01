# PROJECT_OVERVIEW

## 1. Назначение проекта

InternLAB - монолитное Django-приложение для интеллектуального подбора стажировок студентам и просмотра кандидатов работодателями. Проект сделан в формате дипломной работы: главный приоритет - простота, объяснимость, серверный рендеринг и прозрачная бизнес-логика.

Система решает три основные задачи:
- студент заполняет профиль, добавляет навыки, смотрит вакансии, рекомендации и отправляет заявки;
- работодатель заполняет профиль компании, создает вакансии, задает требуемые навыки и рассматривает кандидатов;
- система рассчитывает совпадение студента с вакансией и показывает рекомендации, карту навыков и недостающие навыки.

## 2. Текущий стек

- Python 3.11+
- Django 4.2
- Django ORM
- Django Templates
- Bootstrap 5 через CDN
- Vanilla JavaScript только для небольших UI-улучшений
- SQLite локально по умолчанию
- PostgreSQL при наличии переменных окружения `POSTGRES_*`
- Pillow для `ImageField`
- Django Admin

В проекте нет:
- React/Vue/SPA;
- Django REST Framework;
- Celery/background jobs;
- WebSocket/realtime;
- GraphQL;
- микросервисов.

## 3. Главная архитектурная идея

Архитектура остается классическим Django-монолитом:

```text
Browser
  -> Django URLConf
  -> Django Views
  -> Forms / Services
  -> Django ORM Models
  -> SQLite/PostgreSQL
  -> Django Templates
  -> Bootstrap UI
```

Бизнес-логика, которая важна для диплома, вынесена в сервисный слой:
- `apps/matching/services.py` - расчет совпадения, рекомендации, карта навыков, недостающие навыки.

CRUD-логика в основном находится во views/forms соответствующих apps.

## 4. Структура проекта

```text
InternLAB/
  manage.py
  AGENTS.md
  README.md
  requirements.txt
  config/
    settings.py
    urls.py
    wsgi.py
    asgi.py
  apps/
    users/
    profiles/
    skills/
    vacancies/
    applications/
    matching/
    core/
  templates/
    base.html
    registration/
    core/
    users/
    profiles/
    skills/
    vacancies/
    applications/
    matching/
  static/
    css/
      app.css
      applications_employer.css
      matching_recommendations.css
      vacancies_public_list.css
  media/
    avatars/
```

## 5. Роли

### Student

Может:
- регистрироваться и входить;
- создавать/редактировать профиль;
- загружать аватар;
- добавлять/редактировать/удалять свои навыки;
- просматривать опубликованные вакансии;
- сохранять вакансии в избранное;
- смотреть рекомендации;
- отправлять заявки на опубликованные вакансии;
- смотреть свои заявки;
- добавлять проекты в портфолио.

### Employer

Может:
- регистрироваться и входить;
- создавать/редактировать профиль компании;
- загружать логотип компании;
- создавать, редактировать, публиковать, закрывать и архивировать свои вакансии;
- добавлять требуемые навыки вакансии;
- смотреть заявки на свои вакансии;
- менять статус заявок.

### Admin

Использует Django Admin:
- управление пользователями;
- управление профилями;
- управление навыками;
- управление вакансиями;
- управление заявками.

## 6. Основные пользовательские флоу

### Регистрация студента

```text
/register/
  -> UserRegistrationForm
  -> CustomUser(role=student)
  -> login()
  -> /profiles/student/
  -> если профиля нет: redirect на /profiles/student/create/
```

### Регистрация работодателя

```text
/register/
  -> UserRegistrationForm
  -> CustomUser(role=employer)
  -> login()
  -> /employer/dashboard/
```

### Публикация вакансии

```text
Employer
  -> /vacancies/employer/create/
  -> VacancyForm
  -> Vacancy
  -> VacancySkill bulk_create(selected skills)
  -> detail page
  -> publish/close/archive status actions
```

### Рекомендации студенту

```text
StudentProfile
  -> get_recommended_vacancies()
  -> calculate_vacancy_match() for every published vacancy
  -> sort by score desc
  -> template: top match + other recommendations + skill wheel + missing skills
```

## 7. Готовый функционал

- Custom user model с email login и ролями.
- Registration/login/logout.
- Role-based access control через `role_required`.
- StudentProfile и EmployerProfile.
- Avatar/logo upload через `ImageField`.
- StudentProject как простой конструктор портфолио.
- Skills CRUD для студента.
- Vacancy CRUD для работодателя.
- VacancySkill CRUD.
- Public vacancy list/detail.
- Search по вакансии: title, description, required skills.
- Favorite vacancies для студентов.
- Matching service.
- Recommendations page.
- Skill wheel with student-vs-market radar data.
- Next skill recommendations.
- Applications module.
- Employer dashboard.
- Employer candidates page.
- Demo seed command.
- Bootstrap 5 UI, light/dark theme через localStorage.

## 8. Документы handoff

Этот файл дает общий обзор. Для разработки использовать также:
- `ARCHITECTURE.md`
- `DATABASE.md`
- `API_REFERENCE.md`
- `BUSINESS_LOGIC.md`
- `SECURITY_AUDIT.md`
- `TECH_DEBT.md`
- `SAFE_DEVELOPMENT_GUIDE.md`
- `AI_HANDOFF.md`

