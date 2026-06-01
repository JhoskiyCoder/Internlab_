# API_REFERENCE

## 1. Important note

This project is not API-first. Most routes return server-rendered HTML. The word "API" here means the HTTP interface exposed by Django URL patterns.

There is no Django REST Framework and no serializers.

## 2. Core routes

| URL | Method | View | Auth | Response | Side effects |
| --- | --- | --- | --- | --- | --- |
| `/` | GET | `core.views.home` | Public | HTML home page | None |
| `/about/` | GET | `core.views.about_project` | Public | HTML | None |
| `/faq/` | GET | `core.views.faq` | Public | HTML | None |
| `/contacts/` | GET | `core.views.contacts` | Public | HTML | None |

## 3. Auth routes

| URL | Method | View | Auth | Request | Response | Side effects |
| --- | --- | --- | --- | --- | --- | --- |
| `/register/` | GET | `users.RegisterView` | Anonymous | None | Registration HTML | None |
| `/register/` | POST | `users.RegisterView` | Anonymous | `email`, `role`, `password1`, `password2` | Redirect by role | Creates user, logs user in |
| `/login/` | GET | `users.RoleLoginView` | Anonymous | None | Login HTML | None |
| `/login/` | POST | `users.RoleLoginView` | Anonymous | `username` email, `password` | Redirect by role | Creates auth session |
| `/logout/` | POST/GET by Django view | `LogoutView` | Authenticated | None | Redirect `/` | Ends session |
| `/student/dashboard/` | GET | `users.student_dashboard` | Student | None | HTML | None |
| `/employer/dashboard/` | GET | `users.employer_dashboard` | Employer | None | HTML dashboard | Reads metrics |

Redirect by role:
- student -> `/profiles/student/`
- employer -> `/employer/dashboard/`
- admin/other -> `/`

## 4. Profile routes

| URL | Method | View | Auth | Request | Response | Side effects |
| --- | --- | --- | --- | --- | --- | --- |
| `/profiles/student/` | GET | `profiles.student_profile_detail` | Student | None | HTML profile | Redirects to create if missing |
| `/profiles/student/` | POST | `profiles.student_profile_detail` | Student | `form_type` variants | Redirect profile tab | Updates profile/settings/languages/projects |
| `/profiles/student/create/` | GET | `profiles.student_profile_create` | Student | None | Form HTML | None |
| `/profiles/student/create/` | POST | `profiles.student_profile_create` | Student | profile fields + optional avatar | Redirect detail | Creates StudentProfile |
| `/profiles/student/edit/` | GET | `profiles.student_profile_edit` | Student | None | Form HTML | None |
| `/profiles/student/edit/` | POST | `profiles.student_profile_edit` | Student | profile fields + optional avatar | Redirect detail | Updates own StudentProfile |
| `/profiles/employer/` | GET | `profiles.employer_profile_detail` | Employer | None | HTML profile | Redirects to create if missing |
| `/profiles/employer/create/` | GET | `profiles.employer_profile_create` | Employer | None | Form HTML | None |
| `/profiles/employer/create/` | POST | `profiles.employer_profile_create` | Employer | company fields + optional logo | Redirect detail | Creates EmployerProfile |
| `/profiles/employer/edit/` | GET | `profiles.employer_profile_edit` | Employer | None | Form HTML | None |
| `/profiles/employer/edit/` | POST | `profiles.employer_profile_edit` | Employer | company fields + optional logo | Redirect detail | Updates own EmployerProfile |

Permissions:
- Student cannot access employer profile pages.
- Employer cannot access student profile pages.
- Profiles are always scoped to `request.user`.

## 5. Skill routes

| URL | Method | View | Auth | Request | Response | Side effects |
| --- | --- | --- | --- | --- | --- | --- |
| `/skills/student/` | GET | `skills.student_skill_list` | Student | None | HTML list | Redirects to profile create if missing |
| `/skills/student/add/` | GET | `skills.student_skill_create` | Student | None | HTML skill picker | None |
| `/skills/student/add/` | POST | `skills.student_skill_create` | Student | hidden `skill`, hidden `level` | Redirect list | Creates StudentSkill |
| `/skills/student/<pk>/edit/` | GET | `skills.student_skill_edit` | Student owner | None | HTML form | None |
| `/skills/student/<pk>/edit/` | POST | `skills.student_skill_edit` | Student owner | `skill`, `level` | Redirect list | Updates own StudentSkill |
| `/skills/student/<pk>/delete/` | GET | `skills.student_skill_delete` | Student owner | None | Confirm HTML | None |
| `/skills/student/<pk>/delete/` | POST | `skills.student_skill_delete` | Student owner | None | Redirect list | Deletes own StudentSkill |

Validation:
- duplicate `student_profile + skill` is blocked by form and DB constraint.
- level must be 1..5.

## 6. Public vacancy routes

| URL | Method | View | Auth | Request | Response | Side effects |
| --- | --- | --- | --- | --- | --- | --- |
| `/vacancies/` | GET | `vacancies.vacancy_public_list` | Public | optional `q` | HTML cards | None |
| `/vacancies/<pk>/` | GET | `vacancies.vacancy_public_detail` | Public | None | HTML detail | 404 if not published |
| `/vacancies/favorites/<pk>/toggle/` | POST | `vacancies.toggle_favorite_vacancy` | Student | optional `next` | Redirect | Creates/deletes FavoriteVacancy |

Search:
- only published vacancies;
- query split by spaces;
- each keyword is applied with OR over title, description, required skill name;
- multiple keywords are combined by chained filters, effectively AND across keywords.

Favorites:
- only students;
- only published vacancies;
- uniqueness by `student_profile + vacancy`.

## 7. Employer vacancy routes

| URL | Method | View | Auth | Request | Response | Side effects |
| --- | --- | --- | --- | --- | --- | --- |
| `/vacancies/employer/` | GET | `employer_vacancy_list` | Employer | optional `status` | HTML list | None |
| `/vacancies/employer/create/` | GET | `employer_vacancy_create` | Employer | None | Vacancy form | None |
| `/vacancies/employer/create/` | POST | `employer_vacancy_create` | Employer | vacancy fields + selected skills | Redirect detail | Creates Vacancy and VacancySkill rows |
| `/vacancies/employer/<pk>/` | GET | `employer_vacancy_detail` | Employer owner | None | HTML detail | None |
| `/vacancies/employer/<pk>/edit/` | GET | `employer_vacancy_edit` | Employer owner | None | Vacancy form | None |
| `/vacancies/employer/<pk>/edit/` | POST | `employer_vacancy_edit` | Employer owner | vacancy fields | Redirect detail | Updates Vacancy fields only |
| `/vacancies/employer/<pk>/publish/` | GET | `employer_vacancy_publish` | Employer owner | None | Confirm HTML | None |
| `/vacancies/employer/<pk>/publish/` | POST | `employer_vacancy_publish` | Employer owner | None | Redirect detail | Sets status `published` |
| `/vacancies/employer/<pk>/close/` | GET | `employer_vacancy_close` | Employer owner | None | Confirm HTML | None |
| `/vacancies/employer/<pk>/close/` | POST | `employer_vacancy_close` | Employer owner | None | Redirect detail | Sets status `closed` |
| `/vacancies/employer/<pk>/archive/` | GET | `employer_vacancy_archive` | Employer owner | None | Confirm HTML | None |
| `/vacancies/employer/<pk>/archive/` | POST | `employer_vacancy_archive` | Employer owner | None | Redirect detail | Sets status `archived` |

Important:
- Employer can only access vacancies where `vacancy.employer == request.user.employer_profile`.
- Edit form does not currently update existing skill requirements; skill management is separate.

## 8. Employer vacancy skill routes

| URL | Method | View | Auth | Request | Response | Side effects |
| --- | --- | --- | --- | --- | --- | --- |
| `/vacancies/employer/<vacancy_pk>/skills/add/` | GET | `employer_vacancy_skill_create` | Employer owner | None | Skill picker HTML | None |
| `/vacancies/employer/<vacancy_pk>/skills/add/` | POST | `employer_vacancy_skill_create` | Employer owner | skill, required_level, is_critical | Redirect vacancy detail | Creates VacancySkill |
| `/vacancies/employer/<vacancy_pk>/skills/<skill_pk>/edit/` | GET | `employer_vacancy_skill_edit` | Employer owner | None | Skill picker HTML | None |
| `/vacancies/employer/<vacancy_pk>/skills/<skill_pk>/edit/` | POST | `employer_vacancy_skill_edit` | Employer owner | skill, required_level, is_critical | Redirect vacancy detail | Updates VacancySkill |
| `/vacancies/employer/<vacancy_pk>/skills/<skill_pk>/delete/` | GET | `employer_vacancy_skill_delete` | Employer owner | None | Confirm HTML | None |
| `/vacancies/employer/<vacancy_pk>/skills/<skill_pk>/delete/` | POST | `employer_vacancy_skill_delete` | Employer owner | None | Redirect vacancy detail | Deletes VacancySkill |

Validation:
- duplicate `vacancy + skill` blocked by form and DB constraint.
- `weight` is hidden and `clean_weight()` returns `1`.

## 9. Application routes

| URL | Method | View | Auth | Request | Response | Side effects |
| --- | --- | --- | --- | --- | --- | --- |
| `/applications/` | GET | `applications_home` | Authenticated | None | Redirect by role | None |
| `/applications/student/` | GET | `student_application_list` | Student | None | HTML list | None |
| `/applications/vacancy/<vacancy_pk>/apply/` | GET | `student_application_create` | Student | None | Apply form | None |
| `/applications/vacancy/<vacancy_pk>/apply/` | POST | `student_application_create` | Student | `cover_letter` | Redirect student list | Creates Application |
| `/applications/employer/` | GET | `employer_application_list` | Employer | optional `status`, `q` | HTML candidate cards | Calculates match per application |
| `/applications/employer/<pk>/` | GET | `employer_application_detail` | Employer owner | None | HTML detail | Shows candidate skills/match |
| `/applications/employer/<pk>/` | POST | `employer_application_detail` | Employer owner | `status` | Redirect detail | Updates application status |

Rules:
- student can apply only to published vacancy;
- duplicate student+vacancy is blocked;
- employer sees only applications for own vacancies.

## 10. Matching routes

| URL | Method | View | Auth | Response | Side effects |
| --- | --- | --- | --- | --- | --- |
| `/matching/student/recommendations/` | GET | `student_recommendations` | Student | HTML recommendations | None |
| `/matching/api/skill-wheel/` | GET | `skill_wheel_api` | Student | JSON | None |
| `/api/skill-wheel/` | GET | `skill_wheel_api` | Student | JSON | None |

JSON example:

```json
{
  "categories": [
    {
      "name": "Frontend",
      "slug": "frontend",
      "score": 20,
      "market_score": 15,
      "skills_total": 5,
      "skills_matched": 1,
      "matched_skills": ["React"],
      "student_total_skills": 5,
      "market_skills_matched": 5,
      "market_skills": ["JavaScript", "TypeScript", "React", "HTML/CSS", "Next.js"],
      "market_vacancies_count": 4,
      "market_total_vacancies": 27
    }
  ]
}
```

