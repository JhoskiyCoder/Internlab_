# SAFE_DEVELOPMENT_GUIDE

## 1. Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py seed_demo_data --reset
python3 manage.py runserver
```

Local URL:

```text
http://127.0.0.1:8000/
```

## 2. Environment variables

Optional PostgreSQL:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
```

Django config:

```text
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
```

If `POSTGRES_DB` is absent, SQLite is used.

## 3. Static and media

Static:
- `STATIC_URL = "static/"`
- `STATICFILES_DIRS = [BASE_DIR / "static"]`

Media:
- `MEDIA_URL = "/media/"`
- `MEDIA_ROOT = BASE_DIR / "media"`

In DEBUG, `config/urls.py` serves media files.

## 4. Demo credentials

Seed command:

```bash
python3 manage.py seed_demo_data --reset
```

Password:

```text
DemoPass123!
```

Students:
- `student.alina@internlab.local`
- `student.bek@internlab.local`
- `student.cholpon@internlab.local`
- `student.daniyar@internlab.local`

Employers:
- `employer.neonsoft@internlab.local`
- `employer.cloudforge@internlab.local`

## 5. Test commands

Run full suite:

```bash
python3 manage.py test
```

Run targeted apps:

```bash
python3 manage.py test apps.users
python3 manage.py test apps.profiles
python3 manage.py test apps.skills
python3 manage.py test apps.vacancies
python3 manage.py test apps.applications
python3 manage.py test apps.matching
```

Run system check:

```bash
python3 manage.py check
```

## 6. Safe development workflow

Before changing behavior:

1. Find URL/view/template/form/model chain.
2. Check tests for the same feature.
3. Check templates for context key usage.
4. If model changes are needed, create migration.
5. Run targeted tests.
6. Run `python3 manage.py check`.

## 7. Files that should be changed together

### Changing student skills

Check:
- `apps/skills/models.py`
- `apps/skills/forms.py`
- `apps/skills/views.py`
- `templates/skills/*`
- `apps/matching/services.py`
- `apps/skills/tests.py`

### Changing skill catalog/category

Check:
- `apps/skills/forms.py`
- `apps/vacancies/forms.py`
- `apps/matching/services.py`
- `apps/core/management/commands/seed_demo_data.py`
- `apps/skills/management/commands/seed_skill_wheel_data.py`
- templates that display categories/icons.

### Changing vacancy cards/list

Check:
- `apps/vacancies/views.py`
- `templates/vacancies/public_vacancy_list.html`
- `templates/vacancies/employer_vacancy_list.html`
- `static/css/vacancies_public_list.css`
- `static/css/app.css`

### Changing vacancy creation

Check:
- `apps/vacancies/forms.py`
- `apps/vacancies/views.py`
- `templates/vacancies/employer_vacancy_form.html`
- `templates/vacancies/employer_vacancy_skill_form.html`
- `apps/vacancies/tests.py`
- `apps/matching/services.py` if requirement fields change.

### Changing applications/candidates

Check:
- `apps/applications/models.py`
- `apps/applications/forms.py`
- `apps/applications/views.py`
- `templates/applications/*`
- `static/css/applications_employer.css`
- `apps/applications/tests.py`
- `apps/matching/services.py`

### Changing matching formula

Check:
- `apps/matching/services.py`
- `apps/matching/tests.py`
- `templates/matching/student_recommendations.html`
- `templates/applications/employer_application_list.html`
- `templates/applications/employer_application_detail.html`
- `templates/vacancies/public_vacancy_list.html`
- `templates/vacancies/public_vacancy_detail.html`
- README/docs.

## 8. Migration strategy

Safe pattern:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py test
```

Before removing fields:
- search with `rg "field_name"`;
- inspect seed command;
- inspect admin;
- inspect forms/templates;
- inspect migrations and tests.

Dangerous fields:
- `CustomUser.email`
- `CustomUser.role`
- `StudentProfile.user`
- `EmployerProfile.user`
- `Skill.name`
- `Skill.category`
- `Vacancy.status`
- `VacancySkill.weight`
- `Application.status`

## 9. Common mistakes

- Forgetting to run migrations after adding models.
- Changing skill names and breaking skill wheel/seed matching.
- Removing `weight` from model while matching still uses it.
- Returning employer pages without ownership filters.
- Showing non-published vacancies to students.
- Forgetting `request.FILES` for avatar/logo forms.
- Adding JS-heavy behavior that violates monolith/server-rendered requirement.
- Updating templates but not the CSS dark mode variant.

## 10. Safe refactoring strategy

Preferred:
- small feature-scoped changes;
- keep old context keys until templates are updated;
- add tests before changing matching/permission logic;
- keep business logic in services;
- keep forms responsible for validation;
- keep views simple and explicit.

Avoid:
- large cross-app rewrites;
- introducing DRF/React/Celery without explicit project decision;
- moving models between apps;
- renaming URLs without redirects/template updates;
- changing role/status choice values casually.

