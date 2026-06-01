from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.matching.services import calculate_vacancy_match
from apps.profiles.models import EmployerProfile, StudentProfile
from apps.profiles.models import StudentProject
from apps.users.permissions import role_required
from apps.vacancies.models import Vacancy

from .forms import ApplicationCreateForm, ApplicationStatusForm
from .models import Application


@login_required
def applications_home(request):
    if request.user.role == "student":
        return redirect("applications:student_list")
    if request.user.role == "employer":
        return redirect("applications:employer_list")
    return redirect("core:home")


def _get_student_profile_or_redirect(request):
    profile = StudentProfile.objects.filter(user=request.user).first()
    if not profile:
        messages.info(request, "Сначала заполните профиль студента.")
        return None, redirect("profiles:student_profile_create")
    return profile, None


def _get_employer_profile_or_redirect(request):
    profile = EmployerProfile.objects.filter(user=request.user).first()
    if not profile:
        messages.info(request, "Сначала заполните профиль работодателя.")
        return None, redirect("profiles:employer_profile_create")
    return profile, None


@login_required
@role_required("student")
def student_application_list(request):
    profile, redirect_response = _get_student_profile_or_redirect(request)
    if redirect_response:
        return redirect_response

    applications = Application.objects.filter(student=profile).select_related("vacancy", "vacancy__employer")
    return render(request, "applications/student_application_list.html", {"applications": applications})


@login_required
@role_required("student")
def student_application_create(request, vacancy_pk):
    profile, redirect_response = _get_student_profile_or_redirect(request)
    if redirect_response:
        return redirect_response

    vacancy = get_object_or_404(Vacancy.objects.select_related("employer"), pk=vacancy_pk)

    if vacancy.status != Vacancy.Status.PUBLISHED:
        messages.error(request, "Отклик возможен только на опубликованные вакансии.")
        return redirect("vacancies:public_detail", pk=vacancy.pk)

    if Application.objects.filter(student=profile, vacancy=vacancy).exists():
        messages.info(request, "Вы уже откликались на эту вакансию.")
        return redirect("applications:student_list")

    if request.method == "POST":
        form = ApplicationCreateForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = profile
            application.vacancy = vacancy
            application.status = Application.Status.SUBMITTED
            application.save()
            messages.success(request, "Заявка успешно отправлена.")
            return redirect("applications:student_list")
    else:
        form = ApplicationCreateForm()

    return render(
        request,
        "applications/student_application_form.html",
        {"form": form, "vacancy": vacancy},
    )


@login_required
@role_required("employer")
def employer_application_list(request):
    profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response

    status_filter = request.GET.get("status", "all")
    search_query = request.GET.get("q", "").strip()

    base_applications = Application.objects.filter(vacancy__employer=profile).select_related(
        "student",
        "student__user",
        "vacancy",
    )
    applications = base_applications

    allowed_statuses = {
        Application.Status.SUBMITTED,
        Application.Status.REVIEWING,
        Application.Status.ACCEPTED,
        Application.Status.REJECTED,
    }
    if status_filter in allowed_statuses:
        applications = applications.filter(status=status_filter)

    if search_query:
        applications = applications.filter(
            Q(student__full_name__icontains=search_query)
            | Q(student__user__email__icontains=search_query)
            | Q(vacancy__title__icontains=search_query)
        )

    status_tabs = [
        {"value": "all", "label": "Все", "count": base_applications.count()},
        {
            "value": Application.Status.SUBMITTED,
            "label": "Новые",
            "count": base_applications.filter(status=Application.Status.SUBMITTED).count(),
        },
        {
            "value": Application.Status.REVIEWING,
            "label": "На рассмотрении",
            "count": base_applications.filter(status=Application.Status.REVIEWING).count(),
        },
        {
            "value": Application.Status.ACCEPTED,
            "label": "Принятые",
            "count": base_applications.filter(status=Application.Status.ACCEPTED).count(),
        },
        {
            "value": Application.Status.REJECTED,
            "label": "Отклоненные",
            "count": base_applications.filter(status=Application.Status.REJECTED).count(),
        },
    ]

    application_cards = []
    for application in applications.prefetch_related("vacancy__required_skills__skill"):
        match_result = calculate_vacancy_match(application.student, application.vacancy)
        application_cards.append(
            {
                "application": application,
                "match_score": match_result.score,
            }
        )

    return render(
        request,
        "applications/employer_application_list.html",
        {
            "applications": applications,
            "application_cards": application_cards,
            "status_tabs": status_tabs,
            "active_status": status_filter,
            "search_query": search_query,
        },
    )


@login_required
@role_required("employer")
def employer_application_detail(request, pk):
    profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response

    application = get_object_or_404(
        Application.objects.select_related("student", "student__user", "vacancy", "vacancy__employer").prefetch_related(
            "student__skills__skill",
            "vacancy__required_skills__skill",
        ),
        pk=pk,
        vacancy__employer=profile,
    )
    candidate_skills = application.student.skills.select_related("skill").order_by("skill__category", "skill__name")
    candidate_projects = StudentProject.objects.filter(student_profile=application.student).order_by("-start_date", "-id")
    candidate_languages = [
        language.strip()
        for language in application.student.languages.splitlines()
        if language.strip()
    ]
    average_skill_level = (
        round(sum(item.level for item in candidate_skills) / candidate_skills.count(), 1)
        if candidate_skills.exists()
        else 0
    )
    match_result = calculate_vacancy_match(application.student, application.vacancy)

    if request.method == "POST":
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Статус заявки обновлен.")
            return redirect("applications:employer_detail", pk=application.pk)
    else:
        form = ApplicationStatusForm(instance=application)

    return render(
        request,
        "applications/employer_application_detail.html",
        {
            "application": application,
            "status_form": form,
            "candidate_skills": candidate_skills,
            "candidate_projects": candidate_projects,
            "candidate_languages": candidate_languages,
            "average_skill_level": average_skill_level,
            "match_score": match_result.score,
        },
    )
