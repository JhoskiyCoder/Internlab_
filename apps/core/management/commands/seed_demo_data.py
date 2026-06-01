from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.applications.models import Application
from apps.matching.services import get_recommended_vacancies
from apps.profiles.models import EmployerProfile, StudentProfile
from apps.skills.models import Skill, StudentSkill
from apps.vacancies.models import Vacancy, VacancySkill


class Command(BaseCommand):
    help = "Создать/обновить demo-данные для демонстрации дипломного проекта InternLAB."

    DEMO_PASSWORD = "DemoPass123!"

    SKILL_SPECS = [
        ("Python", Skill.Category.BACKEND, "Язык для backend и data-задач."),
        ("Django", Skill.Category.BACKEND, "Backend-фреймворк для Django monolith."),
        ("JavaScript", Skill.Category.FRONTEND, "Базовый язык frontend-разработки."),
        ("TypeScript", Skill.Category.FRONTEND, "Типизированная разработка frontend-приложений."),
        ("React", Skill.Category.FRONTEND, "Библиотека для UI-компонентов."),
        ("Next.js", Skill.Category.FRONTEND, "Фреймворк для React-приложений."),
        ("HTML", Skill.Category.FRONTEND, "Разметка веб-интерфейсов."),
        ("CSS", Skill.Category.FRONTEND, "Стилизация пользовательских интерфейсов."),
        ("HTML/CSS", Skill.Category.FRONTEND, "Базовая верстка интерфейсов."),
        ("Node.js", Skill.Category.BACKEND, "Backend-разработка на JavaScript runtime."),
        ("Java", Skill.Category.BACKEND, "Backend-разработка корпоративных сервисов."),
        ("SQL", Skill.Category.DATA_SCIENCE, "Работа с данными и запросами."),
        ("PostgreSQL", Skill.Category.BACKEND, "Реляционная СУБД для backend-сервисов."),
        ("Git", Skill.Category.DEVOPS, "Система контроля версий."),
        ("Docker", Skill.Category.DEVOPS, "Контейнеризация приложений."),
        ("Kubernetes", Skill.Category.DEVOPS, "Оркестрация контейнеров."),
        ("Linux", Skill.Category.DEVOPS, "Администрирование и серверная среда."),
        ("AWS", Skill.Category.DEVOPS, "Базовая работа с облачной инфраструктурой."),
        ("REST API", Skill.Category.BACKEND, "Проектирование веб-API."),
        ("HTTP", Skill.Category.CORE_SKILLS, "Понимание протокола HTTP и web-взаимодействия."),
        ("Testing", Skill.Category.BACKEND, "Основы тестирования приложений."),
        ("Algorithms", Skill.Category.BACKEND, "Алгоритмы и структуры данных."),
        ("Kotlin", Skill.Category.MOBILE, "Язык разработки Android-приложений."),
        ("Android", Skill.Category.MOBILE, "Разработка мобильных Android UI."),
        ("CI/CD", Skill.Category.DEVOPS, "Автоматизация сборки и деплоя."),
        ("Pandas", Skill.Category.DATA_SCIENCE, "Обработка и анализ табличных данных."),
        ("NumPy", Skill.Category.DATA_SCIENCE, "Численные вычисления в Python."),
        ("Scikit-learn", Skill.Category.MACHINE_LEARNING, "Классические ML-модели и пайплайны."),
        ("TensorFlow", Skill.Category.MACHINE_LEARNING, "Фреймворк для deep learning."),
        ("PyTorch", Skill.Category.MACHINE_LEARNING, "Фреймворк для deep learning и research."),
        ("OpenCV", Skill.Category.MACHINE_LEARNING, "Компьютерное зрение и обработка изображений."),
        ("Hugging Face", Skill.Category.MACHINE_LEARNING, "NLP-модели и трансформеры."),
    ]

    STUDENT_SPECS = [
        {
            "email": "student.alina@internlab.local",
            "full_name": "Алина Кадырова",
            "phone_number": "+996700111111",
            "university": "КРСУ",
            "faculty": "Информатика и вычислительная техника",
            "course": 3,
            "bio": "Ориентирована на backend-стажировки и web API.",
            "contact_info": "Telegram: @alina_dev",
        },
        {
            "email": "student.bek@internlab.local",
            "full_name": "Бек Туратбеков",
            "phone_number": "+996700222222",
            "university": "AUCA",
            "faculty": "Software Engineering",
            "course": 2,
            "bio": "Frontend-направление, React и интерфейсы.",
            "contact_info": "Telegram: @bek_front",
        },
        {
            "email": "student.cholpon@internlab.local",
            "full_name": "Чолпон Садыкова",
            "phone_number": "+996700333333",
            "university": "МУК",
            "faculty": "Прикладная информатика",
            "course": 4,
            "bio": "Интересуется DevOps и автоматизацией инфраструктуры.",
            "contact_info": "Telegram: @cholpon_ops",
        },
        {
            "email": "student.daniyar@internlab.local",
            "full_name": "Данияр Алимбеков",
            "phone_number": "+996700444444",
            "university": "КГТУ",
            "faculty": "Информационные системы",
            "course": 3,
            "bio": "Сфокусирован на данных, аналитике и SQL.",
            "contact_info": "Telegram: @daniyar_data",
        },
    ]

    EMPLOYER_SPECS = [
        {
            "email": "employer.neonsoft@internlab.local",
            "company_name": "NeonSoft Labs",
            "company_description": "Продуктовая компания с internship-направлениями backend и data.",
            "contact_email": "hr@neonsoft.example",
            "website": "https://neonsoft.example",
        },
        {
            "email": "employer.cloudforge@internlab.local",
            "company_name": "CloudForge Studio",
            "company_description": "Команда, развивающая frontend и DevOps стажировки.",
            "contact_email": "careers@cloudforge.example",
            "website": "https://cloudforge.example",
        },
    ]

    VACANCY_SPECS = [
        {
            "title": "Backend стажер (Python/Django)",
            "employer": "NeonSoft Labs",
            "description": "Разработка backend-модулей, API и работа с БД.",
            "requirements_text": "Python, Django, REST API, PostgreSQL, Git.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Frontend стажер (React)",
            "employer": "CloudForge Studio",
            "description": "Разработка интерфейсов и интеграция с API.",
            "requirements_text": "React, JavaScript, HTML, CSS, Git.",
            "location": "Кыргызстан",
            "internship_type": Vacancy.InternshipType.REMOTE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "DevOps стажер (Docker/Linux)",
            "employer": "CloudForge Studio",
            "description": "Поддержка CI/CD, контейнеров и тестовых окружений.",
            "requirements_text": "Docker, Linux, Git, CI/CD, Python.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.ONSITE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Data Analyst стажер (SQL/Python)",
            "employer": "NeonSoft Labs",
            "description": "Подготовка датасетов и аналитических SQL-отчетов.",
            "requirements_text": "SQL, Python, PostgreSQL, Testing.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Mobile стажер (Android/Kotlin)",
            "employer": "CloudForge Studio",
            "description": "Участие в разработке Android-приложения.",
            "requirements_text": "Kotlin, Android, Algorithms, Git.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.ONSITE,
            "status": Vacancy.Status.CLOSED,
        },
        {
            "title": "QA стажер (Testing/Python)",
            "employer": "NeonSoft Labs",
            "description": "Подготовка тест-кейсов и автоматизация базовых тестов.",
            "requirements_text": "Testing, Python, SQL, Git.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "API Integration стажер",
            "employer": "NeonSoft Labs",
            "description": "Интеграция внешних сервисов и сопровождение REST API.",
            "requirements_text": "REST API, Python, Django, Git.",
            "location": "Кыргызстан",
            "internship_type": Vacancy.InternshipType.REMOTE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Data Pipeline стажер",
            "employer": "NeonSoft Labs",
            "description": "Поддержка ETL-процессов и подготовка витрин данных.",
            "requirements_text": "SQL, PostgreSQL, Python, Algorithms.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "DevOps Automation стажер",
            "employer": "CloudForge Studio",
            "description": "Автоматизация CI/CD и контейнерных окружений.",
            "requirements_text": "Docker, Linux, CI/CD, Git, Python.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.ONSITE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Web Generalist стажер",
            "employer": "CloudForge Studio",
            "description": "Поддержка fullstack-задач на frontend и backend.",
            "requirements_text": "JavaScript, HTML, CSS, Python, REST API.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.DRAFT,
        },
        {
            "title": "Backend API стажер (Django/SQL)",
            "employer": "NeonSoft Labs",
            "description": "Разработка внутренних API и оптимизация SQL-запросов.",
            "requirements_text": "Django, Python, SQL, PostgreSQL, Git.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Frontend UI стажер (HTML/CSS/JS)",
            "employer": "CloudForge Studio",
            "description": "Разработка интерфейсов, верстка и улучшение UX компонентов.",
            "requirements_text": "JavaScript, HTML, CSS, Git, React.",
            "location": "Кыргызстан",
            "internship_type": Vacancy.InternshipType.REMOTE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Support Engineer стажер (Linux/SQL)",
            "employer": "NeonSoft Labs",
            "description": "Поддержка внутренних систем и базовые задачи эксплуатации.",
            "requirements_text": "Linux, SQL, Git, Testing.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.ONSITE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Product Analytics стажер",
            "employer": "NeonSoft Labs",
            "description": "Анализ продуктовых метрик и построение отчетов для команды продукта.",
            "requirements_text": "SQL, Python, Testing, Algorithms.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Platform Operations стажер",
            "employer": "CloudForge Studio",
            "description": "Поддержка инфраструктуры и базовые задачи по автоматизации процессов.",
            "requirements_text": "Docker, Linux, CI/CD, Git.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.ONSITE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Junior Mobile QA стажер",
            "employer": "CloudForge Studio",
            "description": "Тестирование мобильных экранов и API-интеграций Android-приложения.",
            "requirements_text": "Android, Testing, Git, REST API.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.ARCHIVED,
        },
        {
            "title": "ML Engineer стажер (Python/Scikit-learn)",
            "employer": "NeonSoft Labs",
            "description": "Подготовка ML-фичей, обучение baseline-моделей и оценка метрик.",
            "requirements_text": "Python, Scikit-learn, Pandas, NumPy, SQL.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "NLP стажер (Transformers)",
            "employer": "NeonSoft Labs",
            "description": "Работа с текстовыми данными и моделями NLP в прод-пайплайне.",
            "requirements_text": "Python, Hugging Face, Scikit-learn, SQL, Git.",
            "location": "Кыргызстан",
            "internship_type": Vacancy.InternshipType.REMOTE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Computer Vision стажер",
            "employer": "CloudForge Studio",
            "description": "Подготовка датасетов изображений и эксперименты с CV-моделями.",
            "requirements_text": "Python, OpenCV, PyTorch, NumPy, Git.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.ONSITE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "MLOps стажер (ML + Docker)",
            "employer": "CloudForge Studio",
            "description": "Сборка ML-сервисов, контейнеризация и CI/CD для моделей.",
            "requirements_text": "Python, Docker, CI/CD, TensorFlow, Linux.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Kubernetes Platform стажер",
            "employer": "CloudForge Studio",
            "description": "Помощь в поддержке контейнерной платформы и учебных Kubernetes-кластеров.",
            "requirements_text": "Kubernetes, Docker, Linux, CI/CD, AWS.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Cloud Infrastructure стажер (AWS)",
            "employer": "CloudForge Studio",
            "description": "Базовая настройка облачных окружений и сопровождение инфраструктурных задач.",
            "requirements_text": "AWS, Linux, Docker, Kubernetes, CI/CD.",
            "location": "Кыргызстан",
            "internship_type": Vacancy.InternshipType.REMOTE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "CI/CD стажер",
            "employer": "CloudForge Studio",
            "description": "Поддержка пайплайнов сборки, тестирования и деплоя учебных сервисов.",
            "requirements_text": "CI/CD, Docker, Git, Linux, Testing.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.ONSITE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "ML Research стажер (PyTorch)",
            "employer": "NeonSoft Labs",
            "description": "Эксперименты с baseline-моделями, подготовка признаков и сравнение метрик.",
            "requirements_text": "PyTorch, Python, NumPy, Scikit-learn, Pandas.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Deep Learning стажер (TensorFlow)",
            "employer": "NeonSoft Labs",
            "description": "Поддержка учебных deep learning экспериментов и подготовка простых ML-сервисов.",
            "requirements_text": "TensorFlow, Python, NumPy, Docker, Git.",
            "location": "Кыргызстан",
            "internship_type": Vacancy.InternshipType.REMOTE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Computer Vision Dataset стажер",
            "employer": "CloudForge Studio",
            "description": "Разметка и подготовка датасетов для задач компьютерного зрения.",
            "requirements_text": "OpenCV, Python, PyTorch, NumPy, Linux.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Frontend TypeScript стажер",
            "employer": "CloudForge Studio",
            "description": "Разработка типизированных UI-компонентов и страниц на React.",
            "requirements_text": "TypeScript, React, JavaScript, HTML/CSS, Next.js.",
            "location": "Кыргызстан",
            "internship_type": Vacancy.InternshipType.REMOTE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Fullstack Node.js стажер",
            "employer": "NeonSoft Labs",
            "description": "Работа с простыми backend-сервисами и интеграция frontend с API.",
            "requirements_text": "Node.js, REST API, PostgreSQL, JavaScript, Git.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Java Backend стажер",
            "employer": "NeonSoft Labs",
            "description": "Поддержка backend-модулей, работа с API и базовыми алгоритмическими задачами.",
            "requirements_text": "Java, REST API, PostgreSQL, Algorithms, Git.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.ONSITE,
            "status": Vacancy.Status.PUBLISHED,
        },
        {
            "title": "Data Science стажер (Pandas/NumPy)",
            "employer": "NeonSoft Labs",
            "description": "Анализ данных, подготовка признаков и проверка простых ML-гипотез.",
            "requirements_text": "Python, Pandas, NumPy, SQL, Scikit-learn.",
            "location": "Бишкек",
            "internship_type": Vacancy.InternshipType.HYBRID,
            "status": Vacancy.Status.PUBLISHED,
        },
    ]

    STUDENT_SKILL_LEVELS = {
        "Алина Кадырова": {
            "Python": 5,
            "Django": 5,
            "REST API": 4,
            "PostgreSQL": 4,
            "SQL": 4,
            "Git": 4,
            "Testing": 3,
            "Algorithms": 3,
            "Pandas": 2,
            "Scikit-learn": 2,
        },
        "Бек Туратбеков": {
            "JavaScript": 5,
            "React": 5,
            "HTML": 5,
            "CSS": 5,
            "Git": 4,
            "Python": 2,
            "REST API": 3,
        },
        "Чолпон Садыкова": {
            "Docker": 5,
            "Linux": 5,
            "CI/CD": 4,
            "Git": 5,
            "Python": 3,
            "Testing": 3,
            "REST API": 2,
            "TensorFlow": 2,
        },
        "Данияр Алимбеков": {
            "SQL": 5,
            "Python": 4,
            "PostgreSQL": 4,
            "Testing": 4,
            "Algorithms": 4,
            "Git": 3,
            "Django": 2,
            "Pandas": 5,
            "NumPy": 4,
            "Scikit-learn": 4,
            "TensorFlow": 3,
            "PyTorch": 3,
            "OpenCV": 2,
            "Hugging Face": 3,
        },
    }

    VACANCY_SKILL_REQUIREMENTS = {
        "Backend стажер (Python/Django)": [
            ("Python", 4, 10, True),
            ("Django", 4, 9, True),
            ("REST API", 3, 8, True),
            ("PostgreSQL", 3, 6, False),
            ("Git", 3, 4, False),
            ("Testing", 2, 3, False),
        ],
        "Frontend стажер (React)": [
            ("React", 4, 10, True),
            ("JavaScript", 4, 9, True),
            ("HTML", 3, 6, False),
            ("CSS", 3, 6, False),
            ("Git", 2, 3, False),
            ("REST API", 2, 2, False),
        ],
        "DevOps стажер (Docker/Linux)": [
            ("Docker", 4, 10, True),
            ("Linux", 4, 9, True),
            ("CI/CD", 3, 7, True),
            ("Git", 3, 5, False),
            ("Python", 2, 3, False),
        ],
        "Data Analyst стажер (SQL/Python)": [
            ("SQL", 4, 10, True),
            ("Python", 3, 8, True),
            ("PostgreSQL", 3, 6, False),
            ("Testing", 2, 4, False),
            ("Algorithms", 2, 3, False),
        ],
        "Mobile стажер (Android/Kotlin)": [
            ("Kotlin", 3, 9, True),
            ("Android", 3, 8, True),
            ("Algorithms", 3, 5, False),
            ("Git", 2, 3, False),
        ],
        "QA стажер (Testing/Python)": [
            ("Testing", 4, 10, True),
            ("Python", 3, 7, True),
            ("SQL", 2, 5, False),
            ("Git", 2, 3, False),
        ],
        "API Integration стажер": [
            ("REST API", 4, 10, True),
            ("Python", 3, 8, True),
            ("Django", 3, 7, False),
            ("Git", 2, 3, False),
        ],
        "Data Pipeline стажер": [
            ("SQL", 4, 10, True),
            ("PostgreSQL", 4, 8, True),
            ("Python", 3, 7, True),
            ("Algorithms", 3, 5, False),
            ("Git", 2, 3, False),
        ],
        "DevOps Automation стажер": [
            ("Docker", 4, 10, True),
            ("Linux", 4, 9, True),
            ("CI/CD", 4, 8, True),
            ("Git", 3, 5, False),
            ("Python", 2, 3, False),
        ],
        "Web Generalist стажер": [
            ("JavaScript", 3, 8, True),
            ("HTML", 3, 6, False),
            ("CSS", 3, 6, False),
            ("Python", 2, 5, False),
            ("REST API", 2, 4, False),
        ],
        "Backend API стажер (Django/SQL)": [
            ("Django", 4, 10, True),
            ("Python", 4, 9, True),
            ("SQL", 3, 7, True),
            ("PostgreSQL", 3, 6, False),
            ("Git", 3, 4, False),
        ],
        "Frontend UI стажер (HTML/CSS/JS)": [
            ("JavaScript", 4, 10, True),
            ("HTML", 4, 7, True),
            ("CSS", 4, 7, True),
            ("Git", 2, 3, False),
            ("React", 2, 4, False),
        ],
        "Support Engineer стажер (Linux/SQL)": [
            ("Linux", 4, 10, True),
            ("SQL", 3, 7, True),
            ("Git", 2, 4, False),
            ("Testing", 2, 4, False),
        ],
        "Product Analytics стажер": [
            ("SQL", 4, 10, True),
            ("Python", 3, 8, True),
            ("Testing", 3, 6, False),
            ("Algorithms", 3, 5, False),
        ],
        "Platform Operations стажер": [
            ("Docker", 4, 10, True),
            ("Linux", 4, 9, True),
            ("CI/CD", 3, 8, True),
            ("Git", 3, 5, False),
        ],
        "Junior Mobile QA стажер": [
            ("Android", 3, 9, True),
            ("Testing", 3, 8, True),
            ("Git", 2, 4, False),
            ("REST API", 2, 4, False),
        ],
        "ML Engineer стажер (Python/Scikit-learn)": [
            ("Scikit-learn", 4, 10, True),
            ("PyTorch", 3, 8, True),
            ("TensorFlow", 3, 6, False),
            ("Python", 4, 4, True),
            ("Pandas", 3, 3, False),
        ],
        "NLP стажер (Transformers)": [
            ("Hugging Face", 4, 10, True),
            ("PyTorch", 3, 7, True),
            ("TensorFlow", 2, 6, False),
            ("Python", 3, 4, True),
            ("Git", 2, 3, False),
        ],
        "Computer Vision стажер": [
            ("Python", 4, 10, True),
            ("OpenCV", 4, 9, True),
            ("PyTorch", 3, 8, True),
            ("NumPy", 3, 5, False),
            ("Git", 2, 3, False),
        ],
        "MLOps стажер (ML + Docker)": [
            ("Python", 4, 10, True),
            ("Docker", 4, 9, True),
            ("CI/CD", 3, 8, True),
            ("TensorFlow", 3, 6, False),
            ("Linux", 3, 5, False),
        ],
        "Kubernetes Platform стажер": [
            ("Kubernetes", 3, 10, True),
            ("Docker", 4, 9, True),
            ("Linux", 4, 8, True),
            ("CI/CD", 3, 7, False),
            ("AWS", 2, 5, False),
        ],
        "Cloud Infrastructure стажер (AWS)": [
            ("AWS", 3, 10, True),
            ("Linux", 4, 8, True),
            ("Docker", 3, 7, False),
            ("Kubernetes", 2, 6, False),
            ("CI/CD", 2, 5, False),
        ],
        "CI/CD стажер": [
            ("CI/CD", 4, 10, True),
            ("Docker", 3, 8, True),
            ("Git", 3, 6, False),
            ("Linux", 3, 6, False),
            ("Testing", 2, 4, False),
        ],
        "ML Research стажер (PyTorch)": [
            ("PyTorch", 3, 10, True),
            ("TensorFlow", 3, 7, False),
            ("Scikit-learn", 3, 6, False),
            ("Python", 4, 4, True),
            ("NumPy", 3, 3, False),
        ],
        "Deep Learning стажер (TensorFlow)": [
            ("TensorFlow", 3, 10, True),
            ("PyTorch", 3, 8, False),
            ("Hugging Face", 2, 6, False),
            ("Python", 4, 4, True),
            ("Docker", 2, 3, False),
        ],
        "Computer Vision Dataset стажер": [
            ("OpenCV", 3, 10, True),
            ("Python", 3, 8, True),
            ("PyTorch", 2, 7, False),
            ("NumPy", 3, 6, False),
            ("Linux", 2, 4, False),
        ],
        "Frontend TypeScript стажер": [
            ("TypeScript", 3, 10, True),
            ("React", 3, 8, True),
            ("JavaScript", 4, 7, False),
            ("HTML/CSS", 3, 6, False),
            ("Next.js", 2, 5, False),
        ],
        "Fullstack Node.js стажер": [
            ("Node.js", 3, 10, True),
            ("REST API", 3, 8, True),
            ("PostgreSQL", 3, 6, False),
            ("JavaScript", 3, 5, False),
            ("Git", 2, 3, False),
        ],
        "Java Backend стажер": [
            ("Java", 3, 10, True),
            ("REST API", 3, 8, True),
            ("PostgreSQL", 3, 6, False),
            ("Algorithms", 3, 5, False),
            ("Git", 2, 3, False),
        ],
        "Data Science стажер (Pandas/NumPy)": [
            ("Python", 4, 10, True),
            ("Pandas", 4, 9, True),
            ("NumPy", 3, 8, False),
            ("SQL", 3, 7, False),
            ("Scikit-learn", 3, 6, False),
        ],
    }

    APPLICATION_SPECS = [
        {
            "student": "Алина Кадырова",
            "vacancy": "Backend стажер (Python/Django)",
            "status": Application.Status.ACCEPTED,
            "cover_letter": "Хочу развиваться в backend и уже работала с Django REST.",
        },
        {
            "student": "Алина Кадырова",
            "vacancy": "Data Analyst стажер (SQL/Python)",
            "status": Application.Status.REVIEWING,
            "cover_letter": "Интересуюсь аналитикой и SQL-оптимизацией.",
        },
        {
            "student": "Бек Туратбеков",
            "vacancy": "Frontend стажер (React)",
            "status": Application.Status.REVIEWING,
            "cover_letter": "Frontend — мое основное направление, есть pet-проекты на React.",
        },
        {
            "student": "Чолпон Садыкова",
            "vacancy": "DevOps стажер (Docker/Linux)",
            "status": Application.Status.SUBMITTED,
            "cover_letter": "Хочу усилить практику по CI/CD и контейнеризации.",
        },
        {
            "student": "Данияр Алимбеков",
            "vacancy": "Data Analyst стажер (SQL/Python)",
            "status": Application.Status.SUBMITTED,
            "cover_letter": "Работаю с SQL и Python в учебных аналитических проектах.",
        },
        {
            "student": "Данияр Алимбеков",
            "vacancy": "Backend стажер (Python/Django)",
            "status": Application.Status.REJECTED,
            "cover_letter": "Пробую себя в backend, готов быстро подтянуть Django.",
        },
        {
            "student": "Данияр Алимбеков",
            "vacancy": "ML Engineer стажер (Python/Scikit-learn)",
            "status": Application.Status.REVIEWING,
            "cover_letter": "Есть учебные ML-проекты на scikit-learn и pandas.",
        },
        {
            "student": "Чолпон Садыкова",
            "vacancy": "MLOps стажер (ML + Docker)",
            "status": Application.Status.SUBMITTED,
            "cover_letter": "Интересно направление MLOps и автоматизация пайплайнов.",
        },
        {
            "student": "Бек Туратбеков",
            "vacancy": "NLP стажер (Transformers)",
            "status": Application.Status.REJECTED,
            "cover_letter": "Хочу попробовать NLP, хотя мой основной профиль frontend.",
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Удалить текущие demo-аккаунты и связанные demo-данные перед сидированием.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_demo_data()

        self.stdout.write(self.style.WARNING("Создание/обновление demo-данных..."))

        skills = self._create_skills()
        employers = self._create_employers()
        students = self._create_students()

        self._sync_student_skills(students, skills)
        vacancies = self._create_vacancies(employers)
        self._sync_vacancy_requirements(vacancies, skills)
        self._sync_applications(students, vacancies)

        self.stdout.write(self.style.SUCCESS("Demo-данные успешно готовы."))
        self.stdout.write(self.style.SUCCESS(f"Общий пароль для demo-аккаунтов: {self.DEMO_PASSWORD}"))
        self._print_demo_accounts()
        self._print_matching_preview(students)

    def _reset_demo_data(self):
        user_model = get_user_model()
        demo_emails = [spec["email"] for spec in self.STUDENT_SPECS] + [spec["email"] for spec in self.EMPLOYER_SPECS]
        deleted_objects, _ = user_model.objects.filter(email__in=demo_emails).delete()

                                                                             
        Vacancy.objects.filter(title__in=[spec["title"] for spec in self.VACANCY_SPECS]).delete()

        self.stdout.write(self.style.WARNING(f"Reset выполнен. Удалено связанных объектов: {deleted_objects}"))

    def _create_skills(self):
        skills = {}
        for name, category, description in self.SKILL_SPECS:
            skill, _ = Skill.objects.update_or_create(
                name=name,
                defaults={"category": category, "description": description},
            )
            skills[name] = skill
        return skills

    def _create_employers(self):
        user_model = get_user_model()
        employers = {}

        for spec in self.EMPLOYER_SPECS:
            user, _ = user_model.objects.update_or_create(
                email=spec["email"],
                defaults={"role": user_model.Role.EMPLOYER, "is_active": True},
            )
            user.set_password(self.DEMO_PASSWORD)
            user.save(update_fields=["password"])

            profile, _ = EmployerProfile.objects.update_or_create(
                user=user,
                defaults={
                    "company_name": spec["company_name"],
                    "company_description": spec["company_description"],
                    "contact_email": spec["contact_email"],
                    "website": spec["website"],
                },
            )
            employers[spec["company_name"]] = profile

        return employers

    def _create_students(self):
        user_model = get_user_model()
        students = {}

        for spec in self.STUDENT_SPECS:
            user, _ = user_model.objects.update_or_create(
                email=spec["email"],
                defaults={"role": user_model.Role.STUDENT, "is_active": True},
            )
            user.set_password(self.DEMO_PASSWORD)
            user.save(update_fields=["password"])

            profile, _ = StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": spec["full_name"],
                    "phone_number": spec["phone_number"],
                    "university": spec["university"],
                    "faculty": spec["faculty"],
                    "course": spec["course"],
                    "bio": spec["bio"],
                    "contact_info": spec["contact_info"],
                },
            )
            students[spec["full_name"]] = profile

        return students

    def _sync_student_skills(self, students, skills):
        for student_name, skill_levels in self.STUDENT_SKILL_LEVELS.items():
            profile = students[student_name]
            expected_skill_ids = {skills[skill_name].id for skill_name in skill_levels}

            StudentSkill.objects.filter(student_profile=profile).exclude(skill_id__in=expected_skill_ids).delete()

            for skill_name, level in skill_levels.items():
                StudentSkill.objects.update_or_create(
                    student_profile=profile,
                    skill=skills[skill_name],
                    defaults={"level": level},
                )

    def _create_vacancies(self, employers):
        vacancies = {}
        for spec in self.VACANCY_SPECS:
            vacancy, _ = Vacancy.objects.update_or_create(
                employer=employers[spec["employer"]],
                title=spec["title"],
                defaults={
                    "description": spec["description"],
                    "requirements_text": spec["requirements_text"],
                    "location": spec["location"],
                    "internship_type": spec["internship_type"],
                    "status": spec["status"],
                },
            )
            vacancies[spec["title"]] = vacancy
        return vacancies

    def _sync_vacancy_requirements(self, vacancies, skills):
        for vacancy_title, requirements in self.VACANCY_SKILL_REQUIREMENTS.items():
            vacancy = vacancies[vacancy_title]
            expected_skill_ids = {skills[skill_name].id for skill_name, _, _, _ in requirements}

            VacancySkill.objects.filter(vacancy=vacancy).exclude(skill_id__in=expected_skill_ids).delete()

            for skill_name, required_level, _weight, is_critical in requirements:
                VacancySkill.objects.update_or_create(
                    vacancy=vacancy,
                    skill=skills[skill_name],
                    defaults={
                        "required_level": required_level,
                        "weight": 1,
                        "is_critical": is_critical,
                    },
                )

    def _sync_applications(self, students, vacancies):
        demo_student_ids = [profile.id for profile in students.values()]
        demo_vacancy_ids = [vacancy.id for vacancy in vacancies.values()]

                                                                                     
        Application.objects.filter(student_id__in=demo_student_ids, vacancy_id__in=demo_vacancy_ids).delete()

        for spec in self.APPLICATION_SPECS:
            Application.objects.update_or_create(
                student=students[spec["student"]],
                vacancy=vacancies[spec["vacancy"]],
                defaults={
                    "cover_letter": spec["cover_letter"],
                    "status": spec["status"],
                },
            )

    def _print_demo_accounts(self):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo-аккаунты для входа:"))
        self.stdout.write("  Студенты:")
        for spec in self.STUDENT_SPECS:
            self.stdout.write(f"    - {spec['email']}")
        self.stdout.write("  Работодатели:")
        for spec in self.EMPLOYER_SPECS:
            self.stdout.write(f"    - {spec['email']}")

    def _print_matching_preview(self, students):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Preview рекомендаций (top-3 опубликованных вакансий):"))
        demo_published_titles = {
            spec["title"] for spec in self.VACANCY_SPECS if spec["status"] == Vacancy.Status.PUBLISHED
        }
        for full_name, profile in students.items():
            recommendations = [
                item
                for item in get_recommended_vacancies(profile)
                if item.vacancy.title in demo_published_titles
            ][:3]
            self.stdout.write(f"  {full_name}:")
            for item in recommendations:
                missing = ", ".join(item.missing_skills) if item.missing_skills else "нет"
                self.stdout.write(f"    - {item.vacancy.title}: {item.score}% | не хватает: {missing}")
