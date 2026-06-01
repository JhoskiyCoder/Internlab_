# BUSINESS_LOGIC

## 1. Matching score

File: `apps/matching/services.py`

Main function:
- `calculate_vacancy_match(student_profile, vacancy)`

Formula:

```text
skill_match = min(student_level / required_level, 1)
score = sum(skill_match * weight) / sum(weight) * 100
```

If a student does not have the skill:

```text
student_level = 0
skill_match = 0
```

If at least one missing skill is marked as critical:

```text
score = score * 0.8
```

Result:
- rounded to 1 decimal place;
- returned as `MatchingResult`.

Return fields:
- `vacancy`
- `score`
- `matched_skills_count`
- `missing_skills`
- `missing_critical_skills`

Important current behavior:
- If vacancy has no requirements, score is `100.0`.
- Missing skills only include skills where student has no `StudentSkill` row.
- If student has a skill but lower level, it is not listed as missing; it only reduces score.
- UI now forces all new/edited `VacancySkill.weight = 1`, but old DB data or admin changes can still create different weights.

## 2. Recommendations

Function:
- `get_recommended_vacancies(student_profile)`

Process:
```text
published vacancies
  -> calculate_vacancy_match for each
  -> sort by score desc
```

Only `Vacancy.Status.PUBLISHED` is used.

Student recommendations page:
- takes top 5 recommendations;
- displays best vacancy separately;
- shows remaining suitable vacancies in a secondary card;
- includes skill wheel and missing skills card.

## 3. Skill wheel

Function:
- `compute_skill_wheel(student_profile)`

Categories:
- Frontend
- Backend
- DevOps
- Data Science
- ML
- Core Skills

Static category skills:

```text
Frontend: JavaScript, TypeScript, React, HTML/CSS, Next.js
Backend: Python, Node.js, Java, PostgreSQL, REST API
DevOps: Docker, Kubernetes, Linux, CI/CD, AWS
Data Science: Python, Pandas, NumPy, SQL, Scikit-learn
ML: PyTorch, TensorFlow, Scikit-learn, Hugging Face, OpenCV
Core Skills: Git, HTTP, Linux, SQL, Algorithms
```

Student line:

```text
score = student_skills_in_category / student_skills_total * 100
```

Meaning:
- this is distribution of student's known skills across directions;
- it is not "coverage of 5 skills in category" anymore.

Market line:

```text
market_score = primary_vacancies_in_category / published_vacancies_total * 100
```

How primary category is detected:
- for each published vacancy, inspect `VacancySkill` requirements;
- sum requirement weights by skill-wheel category;
- choose category with highest sum as vacancy primary direction;
- shared skills like Python, SQL, Git can contribute to multiple categories;
- final selected direction is one category per vacancy.

Important:
- because UI forces weights to `1`, market direction is mostly based on count of category-matching skills.
- if admin or seed introduces different weights, primary direction can change.

## 4. Next skill recommendations

Function:
- `compute_next_skill_recommendations(student_profile, limit=3)`

Process:
```text
published vacancy requirements
  -> exclude student's existing skills
  -> aggregate by skill
  -> market_signal = sum(weight + critical_bonus) + frequency
  -> sort desc
```

Critical bonus:
```text
+2 if requirement.is_critical
```

Priority labels:
- `Важно` if critical count >= 2 or market percent >= 60;
- `Желательно` if market percent >= 35;
- `Плюс` otherwise.

## 5. Vacancy lifecycle

Model statuses:
- `draft`
- `published`
- `closed`
- `archived`

Views allow:
- publish: any owned vacancy -> `published`
- close: any owned vacancy -> `closed`
- archive: any owned vacancy -> `archived`

Current implementation does not enforce a strict state machine. For example, archived can be published again through the publish view if the employer owns it.

Visibility:
- public list/detail shows only `published`;
- recommendations use only `published`;
- applications can be created only for `published`.

## 6. Application lifecycle

Statuses:
- `submitted`
- `reviewing`
- `accepted`
- `rejected`

Rules:
- one student can apply to one vacancy only once;
- duplicate is prevented by app logic and DB `unique_together`;
- employer can update status for applications on own vacancies only.

Current implementation does not enforce allowed transitions. Employer can set any choice value directly from the status form.

## 7. Search logic

Public vacancy search:
- source: `vacancy_public_list`;
- query parameter: `q`;
- split by spaces;
- each keyword filters over:
  - `title__icontains`
  - `description__icontains`
  - `required_skills__skill__name__icontains`
- multiple keywords are applied sequentially, so all keywords must match somewhere.

Employer application search:
- query parameter: `q`;
- filters by:
  - student full name;
  - student email;
  - vacancy title.

## 8. Favorites

Model:
- `FavoriteVacancy`

Rules:
- only student users;
- only published vacancies;
- toggle creates/deletes row;
- unique per student profile and vacancy.

Known UX behavior:
- toggle is server-rendered POST redirect, not AJAX;
- redirect uses hidden `next` value.

## 9. Profile completion

Student profile detail calculates profile completion using:
- avatar;
- basic info;
- skills;
- projects;
- languages.

Languages have a fallback default list in the view when empty, so completion can look more complete than actual persisted user input.

## 10. Demo seed data

Command:

```bash
python manage.py seed_demo_data --reset
```

Creates/updates:
- skills;
- 4 students;
- 2 employers;
- about 30 vacancies;
- vacancy requirements;
- applications with mixed statuses.

Critical:
- command is mostly idempotent by `update_or_create`;
- `--reset` deletes demo users and demo vacancies;
- vacancy requirements are synchronized and non-expected requirements are removed for demo vacancies;
- all vacancy skill weights are reset to `1`.

