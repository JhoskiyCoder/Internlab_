# AI_HANDOFF

## 1. Project philosophy

InternLAB is an academic Django monolith. The goal is not enterprise complexity; the goal is a clean, defendable diploma project.

Always preserve:
- monolithic Django architecture;
- server-rendered templates;
- Bootstrap 5 UI;
- simple forms/views;
- explicit role checks;
- transparent matching service;
- no SPA/API-first rewrite.

## 2. Architecture invariants

Do not break these:

- `AUTH_USER_MODEL = "users.CustomUser"`
- users authenticate by email;
- roles are `student`, `employer`, `admin`;
- students are scoped through `StudentProfile`;
- employers are scoped through `EmployerProfile`;
- students only see published vacancies;
- employers only manage their own vacancies;
- students only edit their own skills/profile/applications;
- matching logic lives in `apps/matching/services.py`;
- templates should not contain core business logic.

## 3. Forbidden refactors unless explicitly requested

Do not:
- convert frontend to React/Vue/SPA;
- introduce DRF as main architecture;
- split backend/frontend repositories;
- remove custom user model;
- remove role-based permission decorators;
- move matching logic into templates;
- remove DB uniqueness constraints;
- change status choice values without migration and full test update;
- remove `VacancySkill.weight` without updating formula/docs/tests;
- delete old profile fields just because UI does not show them.

## 4. Sensitive modules

Most sensitive:
- `apps/users/models.py`
- `apps/users/permissions.py`
- `apps/matching/services.py`
- `apps/vacancies/models.py`
- `apps/vacancies/forms.py`
- `apps/vacancies/views.py`
- `apps/applications/views.py`
- `apps/skills/forms.py`
- `config/settings.py`
- `config/urls.py`

## 5. Hidden dependencies to remember

### Skill catalog

Skill catalog affects:
- student skill picker;
- vacancy skill picker;
- skill wheel categories;
- demo seed data;
- matching explanations.

If adding a technology, update all relevant locations or centralize constants first.

### Weights

The UI currently hides weights and forces them to `1`, but:
- model supports 1..10;
- admin can edit weight;
- matching formula uses weight;
- old tests/docs may talk about weighted formula.

Do not assume weights are gone.

### Profiles

Student and employer flows assume profile exists. If missing, views redirect to create pages.

New role-specific pages should use the same pattern:

```python
profile = StudentProfile.objects.filter(user=request.user).first()
if not profile:
    return redirect("profiles:student_profile_create")
```

or employer equivalent.

### Published-only rule

Student/public views should use:

```python
Vacancy.objects.filter(status=Vacancy.Status.PUBLISHED)
```

Do not show draft/closed/archived vacancies to students.

## 6. Expected coding patterns

Use:
- function-based views;
- `@login_required`;
- `@role_required("student")` or `@role_required("employer")`;
- `get_object_or_404(..., owner=profile)` for ownership;
- Django messages for user feedback;
- ModelForms for validation;
- service functions for non-trivial business logic;
- Bootstrap 5 templates.

Avoid:
- raw SQL;
- global mutable state;
- business logic in templates;
- heavy JavaScript;
- hidden side effects in model `save()` unless very small and documented.

## 7. How to avoid breaking system

Before editing:

1. Use `rg` to find all references.
2. Check the related URL/view/form/template chain.
3. Check tests in the same app.
4. If model fields change, create migrations.
5. Run targeted tests.
6. Run `python3 manage.py check`.

## 8. Feature-specific advice

### Improving UI

Safe files:
- templates under feature folder;
- CSS under `static/css`;
- avoid changing model/view behavior unless required.

Remember dark mode:
- cards;
- badges;
- tables;
- form controls;
- vacancy cards;
- recommendation cards.

### Improving matching

Change only `apps/matching/services.py` first.

Then update:
- matching tests;
- recommendation templates;
- employer candidate templates if output shape changes;
- README/business docs.

### Improving vacancy creation

Be careful with:
- `VacancyForm.selected_skill_configs`;
- `VacancySkillForm.clean_weight`;
- hidden skill/level fields in templates;
- duplicate skill validation.

### Improving applications

Be careful with:
- owner filter `vacancy__employer=profile`;
- duplicate constraint;
- published-only apply rule;
- candidate match calculation.

## 9. Current known risks

- Open redirect possibility in favorite toggle `next`.
- Uploaded images only rely on HTML accept attribute.
- `DEBUG` defaults true.
- `SECRET_KEY` has insecure fallback.
- No pagination.
- No rate limiting.
- Skill catalog duplication.
- Matching can become N+1 heavy as data grows.
- Duplicate skill wheel URL paths.

## 10. Minimum verification after changes

For most changes:

```bash
python3 manage.py check
python3 manage.py test
```

For targeted changes:

```bash
python3 manage.py test apps.matching
python3 manage.py test apps.vacancies
python3 manage.py test apps.applications
python3 manage.py test apps.skills
python3 manage.py test apps.profiles
python3 manage.py test apps.users
```

## 11. Handoff warning to next AI

This project has been iteratively UI-polished. Many templates and CSS classes are custom and interconnected. Do not "clean up" markup aggressively unless you inspect the rendered result and related CSS. The user cares about visual consistency, but also repeatedly asked not to break functionality.

Default to small, careful patches.

