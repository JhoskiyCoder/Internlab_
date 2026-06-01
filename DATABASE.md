# DATABASE

## 1. Database engine

В `config/settings.py` используется условная конфигурация:

- если задан `POSTGRES_DB`, используется PostgreSQL;
- если `POSTGRES_DB` не задан, используется SQLite `db.sqlite3`.

Это важно: локально проект может запускаться на SQLite, но дипломная архитектура описывает PostgreSQL как основную БД.

## 2. ER-style overview

```text
CustomUser 1--1 StudentProfile
CustomUser 1--1 EmployerProfile

StudentProfile 1--N StudentSkill N--1 Skill
StudentProfile 1--N StudentProject
StudentProfile 1--N Application N--1 Vacancy
StudentProfile 1--N FavoriteVacancy N--1 Vacancy

EmployerProfile 1--N Vacancy
Vacancy 1--N VacancySkill N--1 Skill
Vacancy 1--N Application
```

## 3. Models

### `users.CustomUser`

File: `apps/users/models.py`

Extends `AbstractUser`.

Fields:
- `username = None`
- `email` - `EmailField(unique=True)`
- `role` - `CharField(max_length=20, choices=Role.choices, default=student)`
- inherited fields: `password`, `is_active`, `is_staff`, `is_superuser`, `last_login`, `date_joined`, etc.

Choices:
- `student`
- `employer`
- `admin`

Auth:
- `USERNAME_FIELD = "email"`
- `REQUIRED_FIELDS = []`
- manager: `CustomUserManager`

Critical:
- This model is set by `AUTH_USER_MODEL = "users.CustomUser"`.
- Do not replace it after migrations without a full DB migration plan.

### `profiles.StudentProfile`

File: `apps/profiles/models.py`

Fields:
- `user` - `OneToOneField(settings.AUTH_USER_MODEL, related_name="student_profile", on_delete=CASCADE)`
- `full_name` - `CharField(max_length=150)`
- `avatar` - `ImageField(upload_to="avatars/students/", blank=True, null=True)`
- `phone_number` - `CharField(max_length=30, blank=True)`
- `university` - `CharField(max_length=150)`
- `faculty` - `CharField(max_length=150, blank=True)`
- `course` - `PositiveSmallIntegerField(default=1)`
- `bio` - `TextField(blank=True)`
- `languages` - `TextField(blank=True, default="")`
- `contact_info` - `CharField(max_length=255, blank=True)`
- `created_at` - `DateTimeField(auto_now_add=True)`
- `updated_at` - `DateTimeField(auto_now=True)`

Ordering:
- `("full_name",)`

Relations:
- reverse `skills` from `StudentSkill`
- reverse `applications` from `Application`
- reverse `projects` from `StudentProject`
- reverse `favorite_vacancies` from `FavoriteVacancy`

### `profiles.EmployerProfile`

Fields:
- `user` - `OneToOneField(settings.AUTH_USER_MODEL, related_name="employer_profile", on_delete=CASCADE)`
- `company_name` - `CharField(max_length=150)`
- `logo` - `ImageField(upload_to="avatars/employers/", blank=True, null=True)`
- `company_description` - `TextField(blank=True)`
- `contact_email` - `EmailField()`
- `website` - `URLField(blank=True)`
- `created_at` - `DateTimeField(auto_now_add=True)`
- `updated_at` - `DateTimeField(auto_now=True)`

Ordering:
- `("company_name",)`

Relations:
- reverse `vacancies` from `Vacancy`

### `profiles.StudentProject`

Fields:
- `student_profile` - `ForeignKey(StudentProfile, related_name="projects", on_delete=CASCADE)`
- `title` - `CharField(max_length=160)`
- `role` - `CharField(max_length=120, blank=True)`
- `description` - `TextField(blank=True)`
- `start_date` - `DateField(blank=True, null=True)`
- `end_date` - `DateField(blank=True, null=True)`
- `is_current` - `BooleanField(default=False)`
- `created_at` - `DateTimeField(auto_now_add=True)`

Ordering:
- `("-created_at", "-start_date")`

### `skills.Skill`

Fields:
- `name` - `CharField(max_length=120, unique=True)`
- `category` - `CharField(max_length=50, choices=Category.choices, default=Backend)`
- `description` - `TextField(blank=True)`

Choices:
- `Backend`
- `Frontend`
- `DevOps`
- `Data Science`
- `Machine Learning`
- `Core Skills`
- `Mobile`

Ordering:
- `("name",)`

Critical:
- `Skill.name` is the matching identity in many UI/service places.
- Skill names are normalized in services by `strip().lower()`, but DB uniqueness is case-sensitive depending on DB backend.

### `skills.StudentSkill`

Fields:
- `student_profile` - `ForeignKey(StudentProfile, related_name="skills", on_delete=CASCADE)`
- `skill` - `ForeignKey(Skill, related_name="student_entries", on_delete=CASCADE)`
- `level` - `PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])`

Constraints:
- `unique_together = ("student_profile", "skill")`

Ordering:
- `("student_profile", "skill")`

Business meaning:
- Student knows `skill` at level 1..5.

### `vacancies.Vacancy`

Fields:
- `employer` - `ForeignKey(EmployerProfile, related_name="vacancies", on_delete=CASCADE)`
- `title` - `CharField(max_length=180)`
- `description` - `TextField()`
- `requirements_text` - `TextField(blank=True)`
- `location` - `CharField(max_length=150, blank=True)`
- `internship_type` - `CharField(max_length=20, choices=InternshipType.choices, default=hybrid)`
- `status` - `CharField(max_length=20, choices=Status.choices, default=draft)`
- `created_at` - `DateTimeField(auto_now_add=True)`
- `updated_at` - `DateTimeField(auto_now=True)`

Choices:
- `internship_type`: `onsite`, `remote`, `hybrid`
- `status`: `draft`, `published`, `closed`, `archived`

Methods/properties:
- `display_location` normalizes empty/format-like values into `"Не указано"`.

Ordering:
- `("-created_at",)`

### `vacancies.VacancySkill`

Fields:
- `vacancy` - `ForeignKey(Vacancy, related_name="required_skills", on_delete=CASCADE)`
- `skill` - `ForeignKey(Skill, related_name="vacancy_requirements", on_delete=CASCADE)`
- `required_level` - `PositiveSmallIntegerField(validators=[1..5])`
- `weight` - `PositiveSmallIntegerField(default=1, validators=[1..10])`
- `is_critical` - `BooleanField(default=False)`

Constraints:
- `unique_together = ("vacancy", "skill")`

Ordering:
- `("vacancy", "skill")`

Critical:
- UI currently hides `weight` and forces it to `1`.
- Matching formula still uses `weight`.
- Seed command also resets vacancy skill weights to `1`.

### `vacancies.FavoriteVacancy`

Fields:
- `student_profile` - `ForeignKey(StudentProfile, related_name="favorite_vacancies", on_delete=CASCADE)`
- `vacancy` - `ForeignKey(Vacancy, related_name="favorited_by_students", on_delete=CASCADE)`
- `created_at` - `DateTimeField(auto_now_add=True)`

Constraints:
- `unique_together = ("student_profile", "vacancy")`

Ordering:
- `("-created_at",)`

Business meaning:
- Student saved vacancy.

### `applications.Application`

Fields:
- `student` - `ForeignKey(StudentProfile, related_name="applications", on_delete=CASCADE)`
- `vacancy` - `ForeignKey(Vacancy, related_name="applications", on_delete=CASCADE)`
- `cover_letter` - `TextField(blank=True)`
- `status` - `CharField(max_length=20, choices=Status.choices, default=submitted)`
- `created_at` - `DateTimeField(auto_now_add=True)`
- `updated_at` - `DateTimeField(auto_now=True)`

Choices:
- `submitted`
- `reviewing`
- `accepted`
- `rejected`

Constraints:
- `unique_together = ("student", "vacancy")`

Ordering:
- `("-created_at",)`

## 4. Migrations

Current migration files:

```text
apps/users/migrations/0001_initial.py
apps/users/migrations/0002_alter_customuser_role.py

apps/profiles/migrations/0001_initial.py
apps/profiles/migrations/0002_initial.py
apps/profiles/migrations/0003_studentprofile_phone_number.py
apps/profiles/migrations/0004_studentprofile_avatar.py
apps/profiles/migrations/0005_studentproject.py
apps/profiles/migrations/0006_studentprofile_languages.py
apps/profiles/migrations/0007_employerprofile_logo.py

apps/skills/migrations/0001_initial.py
apps/skills/migrations/0002_alter_skill_category.py
apps/skills/migrations/0003_alter_skill_category.py
apps/skills/migrations/0004_alter_skill_category.py

apps/vacancies/migrations/0001_initial.py
apps/vacancies/migrations/0002_alter_vacancy_internship_type_alter_vacancy_status.py
apps/vacancies/migrations/0003_favoritevacancy.py

apps/applications/migrations/0001_initial.py
apps/applications/migrations/0002_initial.py
apps/applications/migrations/0003_alter_application_status.py
```

## 5. Potentially dangerous DB changes

- Changing `AUTH_USER_MODEL` is not safe after initial migration.
- Renaming `Skill.name` can change matching/search behavior and seed idempotency.
- Removing `VacancySkill.weight` breaks matching service unless formula is updated.
- Removing `faculty`, `phone_number`, `contact_info` may break old migrations, admin, seed command, tests, and existing DB rows even if UI no longer shows them.
- Changing status choice values breaks filters, URLs, tests and existing rows.
- Changing `related_name` values breaks templates/views/services.
- Adding strict non-null fields requires defaults or data migration for existing local/demo DB.
- Case-insensitive uniqueness for skills would need careful migration because SQLite/PostgreSQL behave differently.

