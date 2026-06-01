# SECURITY_AUDIT

## 1. Summary

The project is safe enough for an academic local demo, but it is not production-hardened. The largest risks are configuration defaults, file uploads, unvalidated redirect target, lack of rate limiting, and no production static/media strategy.

## 2. Authentication and authorization

### Good

- Custom user model uses email as login.
- Password validation uses Django built-in validators.
- Role access is enforced with `role_required`.
- Ownership checks exist for:
  - student profiles;
  - student skills;
  - employer profiles;
  - employer vacancies;
  - vacancy skills;
  - employer applications.
- Public vacancy detail only exposes published vacancies.
- Applications for employer are filtered by `vacancy__employer=profile`.

### Risks

- `role_required` depends on correct `request.user.role`; if role values are changed, access can break broadly.
- Admin role is not deeply modeled outside Django Admin/dashboard fallback.
- No login throttling/rate limiting.
- No email verification.

## 3. CSRF

Django `CsrfViewMiddleware` is enabled.

Server-rendered forms should be checked to ensure `{% csrf_token %}` exists. Most Django form templates likely include it, but future forms must include CSRF manually.

## 4. SQL injection

Low risk:
- queries use Django ORM;
- search uses `icontains` with ORM parameters;
- no raw SQL was found in inspected code.

## 5. File uploads

Models:
- `StudentProfile.avatar`
- `EmployerProfile.logo`

Forms:
- widgets use `accept="image/*"`.

Risk:
- browser `accept` is not server-side validation;
- no explicit file size validation;
- no MIME/content validation;
- files are served from `MEDIA_ROOT` in DEBUG;
- production media hosting is not configured.

Recommendation:
- add simple validation for max file size and allowed content types;
- store media outside static root;
- in production serve media through web server/object storage.

## 6. Redirect risks

`vacancies.toggle_favorite_vacancy` redirects to:

```python
request.POST.get("next") or reverse("vacancies:public_list")
```

Risk:
- unvalidated `next` can be used as an open redirect if an absolute URL is submitted.

Recommended fix:
- use `django.utils.http.url_has_allowed_host_and_scheme`.

## 7. Configuration risks

Current `config/settings.py`:

```python
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-key-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
```

Risks:
- insecure default secret key;
- debug defaults to true;
- no production security settings:
  - `SECURE_SSL_REDIRECT`
  - `SESSION_COOKIE_SECURE`
  - `CSRF_COOKIE_SECURE`
  - `SECURE_HSTS_SECONDS`
  - `SECURE_BROWSER_XSS_FILTER` is obsolete in modern Django but headers can still be configured;
  - `X_FRAME_OPTIONS` default middleware exists.

For diploma/local demo this is acceptable. For production it is not.

## 8. CORS

No CORS package/config exists. This is fine because the project is not a separate frontend/backend app.

## 9. Permission-sensitive views

Sensitive views:
- `profiles.student_profile_detail`
- `profiles.employer_profile_detail`
- `skills.student_skill_*`
- `vacancies.employer_*`
- `vacancies.toggle_favorite_vacancy`
- `applications.student_application_create`
- `applications.employer_application_*`
- `matching.skill_wheel_api`

Do not remove decorators from these views.

## 10. Admin

Django Admin is exposed at `/admin/`.

Risk:
- default admin path is discoverable.

For diploma this is acceptable. For production:
- enforce strong passwords;
- use HTTPS;
- consider changing admin path or adding extra protection.

## 11. Data integrity protections

DB constraints:
- `StudentSkill(student_profile, skill)` unique.
- `VacancySkill(vacancy, skill)` unique.
- `Application(student, vacancy)` unique.
- `FavoriteVacancy(student_profile, vacancy)` unique.
- `Skill.name` unique.
- `CustomUser.email` unique.

These are important and should not be removed.

## 12. Security checklist before production

- Set `DJANGO_SECRET_KEY`.
- Set `DJANGO_DEBUG=0`.
- Set correct `DJANGO_ALLOWED_HOSTS`.
- Use PostgreSQL.
- Configure HTTPS and secure cookies.
- Validate uploaded image size/type.
- Validate `next` redirect targets.
- Add rate limiting for login/register.
- Configure static/media serving.
- Add backup strategy.
- Add monitoring/logging.

