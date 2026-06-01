from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.applications.models import Application
from apps.skills.models import StudentSkill
from apps.users.permissions import role_required
from apps.vacancies.models import Vacancy

from .forms import EmployerProfileForm, StudentProfileForm, StudentProfileSettingsForm, StudentProjectForm
from .models import EmployerProfile, StudentProfile, StudentProject


@login_required
@role_required("student")
def student_profile_detail(request):
    profile = StudentProfile.objects.filter(user=request.user).first()
    if not profile:
        messages.info(request, "Сначала заполните профиль студента.")
        return redirect("profiles:student_profile_create")

    skills = StudentSkill.objects.filter(student_profile=profile).select_related("skill").order_by("skill__category", "skill__name")
    top_skills = list(skills.order_by("-level", "skill__name")[:3])
    applications = Application.objects.filter(student=profile).select_related("vacancy", "vacancy__employer")
    projects = StudentProject.objects.filter(student_profile=profile)
    avg_skill_level = round(sum(item.level for item in skills) / skills.count(), 1) if skills.exists() else 0

    active_tab = request.GET.get("tab", "profile")
    if active_tab not in {"profile", "applications", "settings"}:
        active_tab = "profile"

    def _parse_languages(raw_value):
        if not raw_value:
            return []
        return [line.strip() for line in raw_value.splitlines() if line.strip()]

    project_form = StudentProjectForm()
    open_settings_modal = False
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "about_quick_edit":
            settings_form = StudentProfileSettingsForm(instance=profile, user=request.user)
            project_form = StudentProjectForm()
            active_tab = "profile"
            profile.bio = request.POST.get("bio", "").strip()
            profile.save(update_fields=["bio", "updated_at"])
            messages.success(request, "Раздел «О себе» обновлен.")
            return redirect(f"{reverse('profiles:student_profile_detail')}?tab=profile")
        elif form_type == "languages_quick_edit":
            settings_form = StudentProfileSettingsForm(instance=profile, user=request.user)
            project_form = StudentProjectForm()
            active_tab = "profile"
            raw_languages = request.POST.get("languages", "")
            normalized_languages = [line.strip() for line in raw_languages.splitlines() if line.strip()]
            profile.languages = "\n".join(normalized_languages)
            profile.save(update_fields=["languages", "updated_at"])
            messages.success(request, "Раздел «Языки» обновлен.")
            return redirect(f"{reverse('profiles:student_profile_detail')}?tab=profile")
        elif form_type == "settings":
            settings_form = StudentProfileSettingsForm(request.POST, request.FILES, instance=profile, user=request.user)
            active_tab = "settings"
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, "Профиль успешно обновлен.")
                return redirect("profiles:student_profile_detail")
            open_settings_modal = True
        elif form_type == "project_create":
            settings_form = StudentProfileSettingsForm(instance=profile, user=request.user)
            project_form = StudentProjectForm(request.POST)
            active_tab = "profile"
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.student_profile = profile
                project.save()
                messages.success(request, "Проект добавлен в портфолио.")
                return redirect(f"{reverse('profiles:student_profile_detail')}?tab=profile")
        elif form_type == "project_delete":
            settings_form = StudentProfileSettingsForm(instance=profile, user=request.user)
            project_pk = request.POST.get("project_pk")
            project = get_object_or_404(StudentProject, pk=project_pk, student_profile=profile)
            project.delete()
            messages.success(request, "Проект удален из портфолио.")
            return redirect(f"{reverse('profiles:student_profile_detail')}?tab=profile")
        else:
            settings_form = StudentProfileSettingsForm(instance=profile, user=request.user)
    else:
        settings_form = StudentProfileSettingsForm(instance=profile, user=request.user)

    languages = _parse_languages(profile.languages) or ["Русский (родной)", "Английский (B2)", "Немецкий (A1)"]

    completion_items = [
        {"label": "Фото профиля", "done": bool(profile.avatar)},
        {"label": "Базовая информация", "done": bool(profile.full_name and profile.university and profile.course)},
        {"label": "Навыки", "done": skills.exists()},
        {"label": "Проекты", "done": projects.exists()},
        {"label": "Языки", "done": bool(languages)},
    ]
    completion_done = sum(1 for item in completion_items if item["done"])
    completion_percent = int((completion_done / len(completion_items)) * 100) if completion_items else 0

    return render(
        request,
        "profiles/student_profile_detail.html",
        {
            "profile": profile,
            "skills": skills,
            "top_skills": top_skills,
            "settings_form": settings_form,
            "project_form": project_form,
            "projects": projects,
            "applications": applications,
            "active_tab": active_tab,
            "languages": languages,
            "languages_raw": "\n".join(languages),
            "completion_items": completion_items,
            "completion_percent": completion_percent,
            "avg_skill_level": avg_skill_level,
            "open_settings_modal": open_settings_modal,
        },
    )


@login_required
@role_required("student")
def student_profile_create(request):
    if StudentProfile.objects.filter(user=request.user).exists():
        return redirect("profiles:student_profile_edit")

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Профиль студента успешно создан.")
            return redirect("profiles:student_profile_detail")
    else:
        form = StudentProfileForm()

    return render(
        request,
        "profiles/student_profile_form.html",
        {"form": form, "title": "Создание профиля студента", "submit_text": "Создать"},
    )


@login_required
@role_required("student")
def student_profile_edit(request):
    profile = StudentProfile.objects.filter(user=request.user).first()
    if not profile:
        return redirect("profiles:student_profile_create")

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен.")

    return redirect(f"{reverse('profiles:student_profile_detail')}?tab=settings")


@login_required
@role_required("employer")
def employer_profile_detail(request):
    profile = EmployerProfile.objects.filter(user=request.user).first()
    if not profile:
        messages.info(request, "Сначала заполните профиль работодателя.")
        return redirect("profiles:employer_profile_create")

    employer_form = EmployerProfileForm(instance=profile)
    open_settings_modal = False
    if request.method == "POST":
        employer_form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        if employer_form.is_valid():
            employer_form.save()
            messages.success(request, "Профиль работодателя успешно обновлен.")
            return redirect("profiles:employer_profile_detail")
        open_settings_modal = True

    vacancies = Vacancy.objects.filter(employer=profile)
    applications = Application.objects.filter(vacancy__employer=profile)
    stats = {
        "total_vacancies": vacancies.count(),
        "published_vacancies": vacancies.filter(status=Vacancy.Status.PUBLISHED).count(),
        "total_applications": applications.count(),
        "new_applications": applications.filter(status=Application.Status.SUBMITTED).count(),
    }
    latest_vacancies = vacancies.annotate(applications_count=Count("applications")).order_by("-created_at")[:3]

    return render(
        request,
        "profiles/employer_profile_detail.html",
        {
            "profile": profile,
            "stats": stats,
            "latest_vacancies": latest_vacancies,
            "employer_form": employer_form,
            "open_settings_modal": open_settings_modal,
        },
    )


@login_required
@role_required("employer")
def employer_profile_create(request):
    if EmployerProfile.objects.filter(user=request.user).exists():
        return redirect("profiles:employer_profile_edit")

    if request.method == "POST":
        form = EmployerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Профиль работодателя успешно создан.")
            return redirect("profiles:employer_profile_detail")
    else:
        form = EmployerProfileForm()

    return render(
        request,
        "profiles/employer_profile_form.html",
        {"form": form, "title": "Создание профиля работодателя", "submit_text": "Создать"},
    )


@login_required
@role_required("employer")
def employer_profile_edit(request):
    profile = EmployerProfile.objects.filter(user=request.user).first()
    if not profile:
        return redirect("profiles:employer_profile_create")

    if request.method == "POST":
        form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль работодателя успешно обновлен.")
            return redirect("profiles:employer_profile_detail")
    else:
        form = EmployerProfileForm(instance=profile)

    return render(
        request,
        "profiles/employer_profile_form.html",
        {"form": form, "title": "Редактирование профиля работодателя", "submit_text": "Сохранить"},
    )
