from django.shortcuts import render
from apps.applications.models import Application
from apps.profiles.models import EmployerProfile, StudentProfile
from apps.vacancies.models import Vacancy


def home(request):
    published_vacancies = Vacancy.objects.filter(status=Vacancy.Status.PUBLISHED)
    latest_vacancies = published_vacancies.select_related("employer").prefetch_related(
        "required_skills__skill"
    )[:3]
    context = {
        "metrics": [
            {"value": published_vacancies.count(), "label": "Вакансий"},
            {"value": EmployerProfile.objects.count(), "label": "Работодателей"},
            {"value": StudentProfile.objects.count(), "label": "Студентов"},
            {"value": Application.objects.count(), "label": "Заявок"},
        ],
        "latest_vacancies": latest_vacancies,
        "directions": [
            {"name": "Frontend", "short": "FE", "level": 78},
            {"name": "Backend", "short": "BE", "level": 86},
            {"name": "DevOps", "short": "DO", "level": 74},
            {"name": "Data Science", "short": "DS", "level": 68},
            {"name": "ML", "short": "ML", "level": 82},
            {"name": "Core Skills", "short": "CS", "level": 90},
        ],
    }
    return render(request, "core/home.html", context)


def about_project(request):
    return render(request, "core/about_project.html")


def faq(request):
    return render(request, "core/faq.html")


def contacts(request):
    return render(request, "core/contacts.html")
