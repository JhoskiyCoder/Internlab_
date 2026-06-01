# AGENTS.md

## Project Title
Web Platform for Intelligent Internship Matching for Students

## Project Type
Academic diploma project (Final Qualification Work, FQW / ВКР)

## Project Goal
Build a monolithic web application that helps students find suitable internships based on their skills and helps employers find relevant candidates.

The system must:
- allow students to create profiles and add skills
- allow employers to publish vacancies and define required skills
- calculate compatibility between student skills and vacancy requirements
- recommend suitable internships to students
- show missing skills for a vacancy
- allow students to apply to vacancies
- allow employers to review student applications

This is an academic project, not a production enterprise system.
The code must be understandable, explainable during diploma defense, and reasonably simple to maintain.

---

## Main Architecture
Use a monolithic Django architecture.

Do NOT split the project into separate frontend and backend applications.
Do NOT build a SPA.
Do NOT use React in this version.

Use:
- Django for backend and server-rendered frontend
- Django Templates for UI rendering
- PostgreSQL as the main database
- Bootstrap 5 for styling
- Django Admin for administrative management

Optional:
- small amount of vanilla JavaScript for UI improvements
- HTMX only if really needed, but prefer plain Django templates first

Architecture flow:
User -> Django Views -> Services / Business Logic -> Models -> PostgreSQL

---

## Main Technology Stack
- Python 3.11+ or compatible stable version
- Django
- PostgreSQL
- Django Templates
- Bootstrap 5
- Django ORM
- Django Admin
- pytest or Django TestCase for tests
- Git

---

## Development Principles
This is a diploma-friendly academic project.

Priorities:
1. clarity
2. correctness
3. simplicity
4. explainability
5. stable functionality

Do NOT overengineer the system.
Do NOT introduce microservices.
Do NOT add unnecessary third-party packages.
Do NOT use complicated frontend state management.
Do NOT implement features that are hard to explain during defense.

Code must look like a solid student diploma project with good structure.

---

## Main Roles
The system has three roles:

### 1. Student
Student can:
- register and log in
- create and edit personal profile
- add skills and skill levels
- browse vacancies
- receive recommended vacancies
- view matching score
- see missing skills
- apply to vacancies
- view own applications

### 2. Employer
Employer can:
- register and log in
- create and edit company profile
- create vacancies
- define required skills and skill levels
- view applications
- review student candidates
- accept or reject applications

### 3. Admin
Admin can:
- manage users
- manage skills
- moderate vacancies
- manage applications
- manage platform content through Django Admin

---

## Functional Scope
The implementation should include the following modules and features.

### Authentication
- user registration
- login
- logout
- role-based access

### Student Profile
- full name
- university
- faculty
- study year / course
- bio / short description
- optional contact info

### Employer Profile
- company name
- company description
- contact info
- optional company website

### Skills
- skill list
- skill categories
- student skill assignment with level
- vacancy required skill assignment with level and weight

### Vacancies
- create vacancy
- edit vacancy
- publish vacancy
- close vacancy
- archive vacancy
- view vacancy details
- list vacancies

### Matching
- calculate compatibility score between student and vacancy
- show missing skills
- rank vacancies by matching score

### Applications
- student submits application
- employer reviews application
- employer accepts or rejects application
- application status tracking

---

## Main Django Apps
Structure the project with a small number of clear apps.

Recommended apps:
- users
- profiles
- skills
- vacancies
- applications
- matching
- core

### App Responsibilities

#### users
Responsible for:
- custom user model
- authentication helpers
- user roles

#### profiles
Responsible for:
- StudentProfile
- EmployerProfile
- profile forms
- profile views

#### skills
Responsible for:
- Skill
- StudentSkill
- skill categories if needed

#### vacancies
Responsible for:
- Vacancy
- VacancySkill
- vacancy management
- vacancy detail pages
- vacancy status handling

#### applications
Responsible for:
- Application
- application submission
- employer review flow

#### matching
Responsible for:
- matching calculation service
- recommendation logic
- missing skills logic

#### core
Responsible for:
- homepage
- shared templates
- base views
- utility functions if needed

---

## Recommended Folder Structure
Use a clean Django monolith structure.

Example:

project_root/
- manage.py
- AGENTS.md
- README.md
- requirements.txt
- config/
- apps/
  - users/
  - profiles/
  - skills/
  - vacancies/
  - applications/
  - matching/
  - core/
- templates/
- static/
- media/

Inside each app keep only necessary files:
- models.py
- views.py
- urls.py
- forms.py
- admin.py
- services.py (only if business logic exists)
- tests.py

If logic grows, splitting into submodules is allowed, but keep structure easy to understand.

---

## Database Design Guidance

### CustomUser
Create a custom user model from the start.

Fields:
- email
- role
- is_active
- is_staff
- date_joined

Use email as login if convenient.

Role values:
- student
- employer
- admin

### StudentProfile
Fields:
- user (OneToOne)
- full_name
- university
- faculty
- course
- bio
- created_at
- updated_at

### EmployerProfile
Fields:
- user (OneToOne)
- company_name
- company_description
- contact_email
- website
- created_at
- updated_at

### Skill
Fields:
- name
- category
- description (optional)

Skill names must be unique.

### StudentSkill
Fields:
- student_profile
- skill
- level

Rules:
- level should be integer, for example from 1 to 5
- unique pair: student_profile + skill

### Vacancy
Fields:
- employer
- title
- description
- requirements_text
- location
- internship_type
- status
- created_at
- updated_at

Status values:
- draft
- published
- closed
- archived

### VacancySkill
Fields:
- vacancy
- skill
- required_level
- weight
- is_critical

Rules:
- required_level should be integer, for example 1 to 5
- weight should influence matching score
- unique pair: vacancy + skill

### Application
Fields:
- student
- vacancy
- cover_letter
- status
- created_at
- updated_at

Status values:
- submitted
- reviewing
- accepted
- rejected

Rules:
- one student should not apply to the same vacancy multiple times unless explicitly allowed
- default behavior: prevent duplicate applications

---

## Matching Logic
This is the key academic feature of the project.

Implement the matching logic in a dedicated service layer.
Do NOT place it directly inside templates or views.
Do NOT hide the logic in model methods if it becomes large.

Create something like:
- apps/matching/services.py

### Main Matching Idea
Each vacancy has required skills.
Each required skill has:
- required level
- weight
- critical flag

Each student has own skills with levels.

The compatibility score should be calculated using a transparent weighted formula.

Suggested formula:

score = sum(skill_match * weight) / sum(weight) * 100

Where:

skill_match = min(student_level / required_level, 1)

If the student does not have a required skill:
- student_level = 0

### Additional Rules
- if a critical skill is missing, reduce total score
- return list of missing skills
- allow score rounding to integer or one decimal place
- recommendations should be sorted by highest score first

### Expected Matching Outputs
For each vacancy recommendation return:
- vacancy object
- matching percentage
- matched skills count
- missing skills list
- whether critical skills are missing

### Academic Framing
This logic should be easy to explain during diploma defense as:
- intelligent recommendation module
- weighted skill matching model
- transparent ranking algorithm
- decision support mechanism

---

## User Interface Requirements
The UI should be simple, clean, and academic.

Use:
- Bootstrap 5
- standard layout with navbar and content area
- forms with validation messages
- tables/cards for data output

Do NOT spend excessive time on advanced design.
Prioritize usability and clarity over visual originality.

### Main Pages

#### Public Pages
- home page
- login
- registration
- about project (optional)

#### Student Pages
- dashboard
- profile page
- edit profile
- manage skills
- vacancy list
- recommended vacancies
- vacancy detail
- my applications

#### Employer Pages
- dashboard
- company profile
- create vacancy
- vacancy list
- vacancy detail
- manage vacancy skills
- received applications
- candidate review page

#### Admin
Use Django Admin as the primary admin panel.

---

## Business Logic Separation
Keep business logic outside of views when it becomes more than basic CRUD.

### Good places for logic
- services.py
- helper functions in matching
- simple utility functions

### Bad places for complex logic
- templates
- huge views.py functions
- forms with too much business logic
- admin actions for core system behavior

---

## View Design
Prefer standard Django function-based views or class-based views.
Choose one style and stay consistent.

Recommended:
- use class-based generic views where convenient
- use simple function-based views when easier to explain

Do NOT build overly abstract view hierarchies.

---

## Forms
Use Django forms / ModelForms.

Requirements:
- clean validation
- clear error messages
- role-based form access
- reusable forms where appropriate

---

## URL Design
Keep URLs readable and academic.

Examples:
- /register/
- /login/
- /student/profile/
- /student/skills/
- /vacancies/
- /vacancies/<id>/
- /recommendations/
- /employer/vacancies/
- /applications/

---

## Permissions and Access Rules
Implement role-based access carefully.

### Student permissions
Student can:
- manage own profile
- manage own skills
- view vacancies
- apply to vacancies
- view own applications

Student cannot:
- create vacancies
- review other students
- access employer pages

### Employer permissions
Employer can:
- manage own company profile
- create and edit own vacancies
- view applications for own vacancies
- accept or reject candidates

Employer cannot:
- edit student profiles
- apply to vacancies

### Admin permissions
Admin has full access through Django Admin.

---

## Status Logic

### Vacancy Status Flow
Suggested flow:
- draft -> published -> closed -> archived

Rules:
- only published vacancies are visible to students
- closed vacancies should not accept new applications
- archived vacancies are hidden from regular listings

### Application Status Flow
Suggested flow:
- submitted -> reviewing -> accepted
- submitted -> reviewing -> rejected

Optional:
- allow direct submitted -> rejected if needed

---

## Testing Requirements
Write tests for critical functionality.

Priority test areas:
1. matching service
2. application creation rules
3. duplicate application prevention
4. vacancy visibility rules
5. role-based access rules

### Matching Test Cases
Must test:
- exact match
- partial match
- no matching skills
- missing critical skill
- vacancy with no required skills
- student with no skills

### Application Test Cases
Must test:
- student can apply to published vacancy
- student cannot apply twice
- student cannot apply to closed vacancy
- employer can review applications for own vacancies only

---

## Documentation Requirements
Keep the project well documented.

### README.md must include:
- project description
- stack
- local setup steps
- environment variables if any
- migration commands
- superuser creation
- brief explanation of matching logic

### In-code documentation
- add docstrings to services and non-trivial functions
- keep comments short and useful
- do not overcomment trivial code

---

## Coding Style Rules

### Python
- follow PEP 8
- use explicit names
- prefer readability
- keep functions reasonably small
- avoid unnecessary inheritance
- avoid premature abstraction
- use clear model field names
- use type hints where helpful, but do not force them everywhere

### Templates
- keep templates clean
- move repeated layout into base template
- use includes for repeated blocks when useful
- avoid business logic in templates

### Bootstrap
- use standard Bootstrap components
- forms should be simple and readable
- cards/tables are acceptable for lists and dashboards

---

## What NOT to Build
Do NOT add these unless explicitly requested later:
- chat system
- real-time notifications
- WebSockets
- microservices
- separate React frontend
- REST API-first architecture
- GraphQL
- complex analytics dashboards
- recommendation based on machine learning
- deployment automation
- payment system

This is a diploma project and should remain feasible.

---

## Academic Presentation Requirements
The final implementation must be easy to explain in terms of:
- system architecture
- main entities
- user roles
- matching algorithm
- vacancy lifecycle
- application lifecycle

The code should support UML diagrams and diploma explanations.

The implementation should map cleanly to:
- use case diagram
- sequence diagram
- activity diagram
- state diagram
- ER diagram

---

## Task Execution Rules for the Agent
When implementing any feature, follow this process:

1. understand AGENTS.md context first
2. keep the architecture monolithic
3. implement one feature at a time
4. avoid unrelated refactoring
5. preserve existing working functionality
6. create or update tests when logic changes
7. summarize changes clearly

When uncertain, prefer the simpler academic solution.

---

## Recommended Development Order
Implement the project in the following order:

1. create Django project structure
2. configure PostgreSQL
3. create custom user model with roles
4. implement student and employer profiles
5. implement skills and student skills
6. implement vacancies and vacancy skills
7. implement applications
8. implement matching service
9. implement role-based views and templates
10. configure Django Admin
11. add tests
12. improve UI with Bootstrap
13. update README

---

## First Tasks for the Agent
When starting the project, prioritize:

### Task 1
Create the Django project structure with the apps:
- users
- profiles
- skills
- vacancies
- applications
- matching
- core

### Task 2
Implement a custom user model with role support.

### Task 3
Implement the core models:
- StudentProfile
- EmployerProfile
- Skill
- StudentSkill
- Vacancy
- VacancySkill
- Application

### Task 4
Register all important models in Django Admin.

### Task 5
Implement the matching service in a separate service module.

### Task 6
Create the basic templates and navigation based on user role.

---

## Final Rule
This project must remain:
- monolithic
- understandable
- academically defendable
- realistically buildable within a student timeline