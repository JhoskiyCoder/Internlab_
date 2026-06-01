from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import CreateView

from apps.applications.models import Application
from apps.profiles.models import EmployerProfile
from apps.vacancies.models import Vacancy

from .forms import UserLoginForm, UserRegistrationForm
from .permissions import role_required


def get_role_home_url(user):
    """Return the default page based on user role."""
    if user.role == "student":
        return reverse("profiles:student_profile_detail")
    if user.role == "employer":
        return reverse("users:employer_dashboard")
    return reverse("core:home")


class RegisterView(CreateView):
    template_name = "registration/register.html"
    form_class = UserRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_role_home_url(request.user))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Регистрация прошла успешно. Добро пожаловать в InternLAB.")
        return response

    def get_success_url(self):
        return get_role_home_url(self.object)


class RoleLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = UserLoginForm

    def get_default_redirect_url(self):
        return get_role_home_url(self.request.user)


@login_required
@role_required("student")
def student_dashboard(request):
    return render(request, "users/student_dashboard.html")


@login_required
@role_required("employer")
def employer_dashboard(request):
    employer_profile = EmployerProfile.objects.filter(user=request.user).first()

    context = {
        "employer_profile": employer_profile,
        "metrics": {
            "total_vacancies": 0,
            "published_vacancies": 0,
            "total_applications": 0,
            "new_applications": 0,
            "reviewing_applications": 0,
            "accepted_applications": 0,
            "draft_vacancies": 0,
            "vacancies_without_skills": 0,
        },
        "recent_applications": [],
        "active_vacancies": [],
        "draft_vacancies": [],
        "vacancies_without_skills": [],
    }

    if employer_profile:
        vacancies = Vacancy.objects.filter(employer=employer_profile)
        applications = Application.objects.filter(vacancy__employer=employer_profile).select_related(
            "student",
            "vacancy",
        )
        context.update(
            {
                "metrics": {
                    "total_vacancies": vacancies.count(),
                    "published_vacancies": vacancies.filter(status=Vacancy.Status.PUBLISHED).count(),
                    "total_applications": applications.count(),
                    "new_applications": applications.filter(status=Application.Status.SUBMITTED).count(),
                    "reviewing_applications": applications.filter(status=Application.Status.REVIEWING).count(),
                    "accepted_applications": applications.filter(status=Application.Status.ACCEPTED).count(),
                    "draft_vacancies": vacancies.filter(status=Vacancy.Status.DRAFT).count(),
                    "vacancies_without_skills": vacancies.annotate(skills_count=Count("required_skills"))
                    .filter(skills_count=0)
                    .count(),
                },
                "recent_applications": applications.order_by("-created_at")[:5],
                "active_vacancies": vacancies.filter(status=Vacancy.Status.PUBLISHED)
                .annotate(applications_count=Count("applications"))
                .order_by("-created_at")[:5],
                "draft_vacancies": vacancies.filter(status=Vacancy.Status.DRAFT).order_by("-created_at")[:3],
                "vacancies_without_skills": vacancies.annotate(skills_count=Count("required_skills"))
                .filter(skills_count=0)
                .order_by("-created_at")[:3],
            }
        )

    return render(request, "users/employer_dashboard.html", context)
