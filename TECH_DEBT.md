# TECH_DEBT

## 1. High-impact technical debt

### Hidden weights mismatch

The database and matching formula support `VacancySkill.weight`, but current UI hides it and forces `weight=1`.

Risk:
- admin or old seed data can introduce non-1 weights;
- matching explanation may not match actual DB data if weights are changed manually.

Safe direction:
- either keep field and clearly document it as academic extension;
- or remove from UI only, but keep service formula documented as weighted.

### Duplicate skill catalogs

Skill category/technology definitions appear in:
- `apps/skills/forms.py`
- `apps/vacancies/forms.py` via `StudentSkillForm.SKILL_CATALOG`
- `apps/matching/services.py` via `SKILL_WHEEL_CATEGORY_SKILLS`
- seed commands.

Risk:
- adding/removing a skill in one place can desync skill picker, seed data and skill wheel.

Safe direction:
- centralize catalog constants in one module, for example `apps/skills/catalog.py`.

### Skill identity is name-based in services

Skill wheel and market matching use normalized names.

Risk:
- renaming a skill changes chart behavior;
- duplicate semantic skills can exist, e.g. `HTML`, `CSS`, `HTML/CSS`.

Safe direction:
- keep names stable or introduce slugs later with data migration.

### N+1/performance concerns

Current matching calculates per vacancy/application:
- public list computes recommendations for all published vacancies;
- employer application list calculates match per application;
- matching service queries student skills per vacancy match.

Acceptable for diploma/demo. Could be slow with thousands of vacancies/applications.

### Application create redirect bug

`student_application_create` gets any vacancy by pk. If status is not published, it redirects to `vacancies:public_detail`, but that detail route only resolves published vacancies, so closed/archived/draft can produce 404 after redirect.

Tests may expect rejection behavior, but UX can be confusing.

### Duplicate skill wheel endpoints

The same view is exposed at:
- `/api/skill-wheel/`
- `/matching/api/skill-wheel/`

Risk:
- future changes may document one but not the other.

### Server-rendered UI with growing inline JS

Some UI behavior is implemented directly in templates.

Risk:
- hard to reuse and test;
- theme/skill picker logic can become fragile.

Keep JS small because project explicitly avoids SPA.

## 2. Medium-impact technical debt

### No pagination

Lists currently render all matching rows:
- public vacancies;
- employer vacancies;
- employer applications;
- student applications.

Acceptable for demo, risky for larger datasets.

### No explicit DB indexes beyond constraints/FKs

Search uses `icontains`, no full-text search.

Acceptable for academic demo. Not scalable.

### Profile fields removed from UI but still in model

Fields like `faculty`, `phone_number`, `contact_info` remain in DB/seed/admin but are not primary UI fields anymore.

Risk:
- future AI may remove them from model and break migrations/seed/admin/tests.

### Demo seed resets selected data

`seed_demo_data --reset` deletes demo accounts and demo vacancies. It is intended, but should not be run against real production-like data if demo emails/titles overlap.

### `templates/.DS_Store`

MacOS metadata file exists under templates. It should ideally be removed and `.DS_Store` added to `.gitignore`.

## 3. UI technical debt

- Bootstrap classes are mixed with custom CSS.
- Several pages have highly customized UI but remain server-rendered.
- CSS split is pragmatic but not a formal design system.
- Dark mode fixes are distributed across CSS files.

Do not attempt a large redesign without checking all role-specific templates.

## 4. Testing debt

Tests cover key flows:
- auth;
- profile access;
- student skills;
- vacancies and vacancy skills;
- applications;
- matching;
- skill wheel.

Gaps:
- favorite redirect safety;
- image upload validation;
- dashboard metrics;
- search edge cases;
- employer vacancy UI filters;
- project portfolio POST actions;
- dark mode/static UI behavior.

## 5. Risky refactors

Avoid broad refactors around:
- custom user model;
- role access decorators;
- profile related names;
- skill catalog;
- vacancy status values;
- application status values;
- matching service return structure;
- template context keys used by heavily customized templates.

