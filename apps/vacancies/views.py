from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from apps.applications.models import Application
from apps.matching.services import get_recommended_vacancies
from apps.profiles.models import EmployerProfile, StudentProfile
from apps.users.permissions import role_required
from .forms import VacancyForm, VacancySkillForm
from .models import FavoriteVacancy, Vacancy, VacancySkill


def _published_label(created_at):
    days = (timezone.now() - created_at).days
    if days <= 3:
        return "Опубликовано недавно"
    if days <= 30:
        return "Опубликовано неделю назад"
    return "Опубликовано более месяца назад"


def _city_from_location(location: str) -> str:
    if not location:
        return "Не указано"
    if location.strip().lower() in {"гибрид", "удаленно", "remote", "hybrid"}:
        return "Не указано"
    normalized = location.replace("/", ",")
    return normalized.split(",")[0].strip() or "Не указано"


def _split_requirement_items(text: str) -> list[str]:
    if not text:
        return []
    normalized = text.replace(";", "\n")
    if "\n" not in normalized and "," in normalized:
        normalized = normalized.replace(",", "\n")
    return [
        item.strip(" .-•") for item in normalized.splitlines() if item.strip(" .-•")
    ]


def vacancy_public_list(request):
    search_query = request.GET.get("q", "").strip()
    keywords = [keyword for keyword in search_query.split() if keyword]
    vacancies = (
        Vacancy.objects.filter(status=Vacancy.Status.PUBLISHED)
        .select_related("employer")
        .prefetch_related("required_skills__skill")
    )
    if keywords:
        for keyword in keywords:
            vacancies = vacancies.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(required_skills__skill__name__icontains=keyword)
            )
        vacancies = vacancies.distinct()
    vacancy_list = list(vacancies)
    scores_by_vacancy_id = {}
    student_banner = None
    favorite_vacancy_ids = []
    applied_vacancy_ids = []
    if request.user.is_authenticated and request.user.role == "student":
        student_profile = StudentProfile.objects.filter(user=request.user).first()
        if student_profile:
            recommendations = get_recommended_vacancies(student_profile)
            scores_by_vacancy_id = {
                item.vacancy.id: item.score for item in recommendations
            }
            favorite_vacancy_ids = list(
                FavoriteVacancy.objects.filter(
                    student_profile=student_profile
                ).values_list("vacancy_id", flat=True)
            )
            student_name = (
                student_profile.full_name.split()[0]
                if student_profile.full_name
                else "студент"
            )
            best_score = max(
                (scores_by_vacancy_id.get(vacancy.id, 0) for vacancy in vacancy_list),
                default=0,
            )
            student_banner = {
                "student_name": student_name,
                "vacancies_count": len(vacancy_list),
                "best_score": best_score,
            }
            applied_vacancy_ids = list(
                Application.objects.filter(
                    student=student_profile,
                    vacancy_id__in=[vacancy.id for vacancy in vacancy_list],
                ).values_list("vacancy_id", flat=True)
            )
    vacancy_cards = [
        {
            "vacancy": vacancy,
            "city": _city_from_location(vacancy.display_location),
            "published_label": _published_label(vacancy.created_at),
            "score": scores_by_vacancy_id.get(vacancy.id),
            "requirement_items": _split_requirement_items(vacancy.requirements_text),
            "already_applied": vacancy.id in applied_vacancy_ids,
        }
        for vacancy in vacancy_list
    ]
    return render(
        request,
        "vacancies/public_vacancy_list.html",
        {
            "vacancy_cards": vacancy_cards,
            "student_banner": student_banner,
            "search_query": search_query,
            "favorite_vacancy_ids": favorite_vacancy_ids,
        },
    )


@login_required
@role_required("student")
def student_favorite_vacancy_list(request):
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    if not student_profile:
        messages.info(request, "Сначала заполните профиль студента.")
        return redirect("profiles:student_profile_create")
    favorites = (
        FavoriteVacancy.objects.filter(
            student_profile=student_profile, vacancy__status=Vacancy.Status.PUBLISHED
        )
        .select_related("vacancy__employer")
        .prefetch_related("vacancy__required_skills__skill")
    )
    favorite_vacancy_ids = list(favorites.values_list("vacancy_id", flat=True))
    favorite_vacancies = [favorite.vacancy for favorite in favorites]
    recommendations = get_recommended_vacancies(student_profile)
    scores_by_vacancy_id = {item.vacancy.id: item.score for item in recommendations}
    applied_vacancy_ids = list(
        Application.objects.filter(
            student=student_profile,
            vacancy_id__in=[vacancy.id for vacancy in favorite_vacancies],
        ).values_list("vacancy_id", flat=True)
    )
    vacancy_cards = [
        {
            "vacancy": vacancy,
            "city": _city_from_location(vacancy.display_location),
            "published_label": _published_label(vacancy.created_at),
            "score": scores_by_vacancy_id.get(vacancy.id),
            "requirement_items": _split_requirement_items(vacancy.requirements_text),
            "already_applied": vacancy.id in applied_vacancy_ids,
        }
        for vacancy in favorite_vacancies
    ]
    return render(
        request,
        "vacancies/student_favorite_vacancy_list.html",
        {"vacancy_cards": vacancy_cards, "favorite_vacancy_ids": favorite_vacancy_ids},
    )


def vacancy_public_detail(request, pk):
    vacancy = get_object_or_404(
        Vacancy.objects.select_related("employer").prefetch_related(
            "required_skills__skill"
        ),
        pk=pk,
        status=Vacancy.Status.PUBLISHED,
    )
    context = {
        "vacancy": vacancy,
        "required_skills": vacancy.required_skills.all(),
        "city": _city_from_location(vacancy.display_location),
        "published_label": _published_label(vacancy.created_at),
        "match_score": None,
        "is_favorite": False,
        "already_applied": False,
        "requirement_items": _split_requirement_items(vacancy.requirements_text),
    }
    if request.user.is_authenticated and request.user.role == "student":
        student_profile = StudentProfile.objects.filter(user=request.user).first()
        if student_profile:
            recommendations = get_recommended_vacancies(student_profile)
            scores_by_vacancy_id = {
                item.vacancy.id: item.score for item in recommendations
            }
            context["match_score"] = scores_by_vacancy_id.get(vacancy.id)
            context["is_favorite"] = FavoriteVacancy.objects.filter(
                student_profile=student_profile, vacancy=vacancy
            ).exists()
            context["already_applied"] = Application.objects.filter(
                student=student_profile, vacancy=vacancy
            ).exists()
    return render(request, "vacancies/public_vacancy_detail.html", context)


@login_required
@role_required("student")
def toggle_favorite_vacancy(request, pk):
    if request.method != "POST":
        return redirect("vacancies:public_list")
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    if not student_profile:
        messages.info(request, "Сначала заполните профиль студента.")
        return redirect("profiles:student_profile_create")
    vacancy = get_object_or_404(Vacancy, pk=pk, status=Vacancy.Status.PUBLISHED)
    favorite_qs = FavoriteVacancy.objects.filter(
        student_profile=student_profile, vacancy=vacancy
    )
    if favorite_qs.exists():
        favorite_qs.delete()
        messages.success(request, "Вакансия удалена из избранного.")
    else:
        FavoriteVacancy.objects.create(student_profile=student_profile, vacancy=vacancy)
        messages.success(request, "Вакансия добавлена в избранное.")
    redirect_to = request.POST.get("next") or reverse("vacancies:public_list")
    return redirect(redirect_to)


def _get_employer_profile_or_redirect(request):
    employer_profile = EmployerProfile.objects.filter(user=request.user).first()
    if not employer_profile:
        messages.info(request, "Сначала заполните профиль работодателя.")
        return (None, redirect("profiles:employer_profile_create"))
    return (employer_profile, None)


def _get_owned_vacancy_or_404(vacancy_pk, employer_profile):
    return get_object_or_404(
        Vacancy.objects.select_related("employer"),
        pk=vacancy_pk,
        employer=employer_profile,
    )


@login_required
@role_required("employer")
def employer_vacancy_list(request):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    status_filter = request.GET.get("status", "all")
    base_vacancies = Vacancy.objects.filter(employer=employer_profile)
    vacancies = base_vacancies.prefetch_related("required_skills__skill").annotate(
        applications_count=Count("applications")
    )
    if status_filter in {
        Vacancy.Status.PUBLISHED,
        Vacancy.Status.DRAFT,
        Vacancy.Status.CLOSED,
        Vacancy.Status.ARCHIVED,
    }:
        vacancies = vacancies.filter(status=status_filter)
    status_tabs = [
        {"value": "all", "label": "Все", "count": base_vacancies.count()},
        {
            "value": Vacancy.Status.PUBLISHED,
            "label": "Активные",
            "count": base_vacancies.filter(status=Vacancy.Status.PUBLISHED).count(),
        },
        {
            "value": Vacancy.Status.DRAFT,
            "label": "Черновики",
            "count": base_vacancies.filter(status=Vacancy.Status.DRAFT).count(),
        },
        {
            "value": Vacancy.Status.CLOSED,
            "label": "Закрытые",
            "count": base_vacancies.filter(status=Vacancy.Status.CLOSED).count(),
        },
        {
            "value": Vacancy.Status.ARCHIVED,
            "label": "Архив",
            "count": base_vacancies.filter(status=Vacancy.Status.ARCHIVED).count(),
        },
    ]
    vacancy_cards = [
        {"vacancy": vacancy, "published_label": _published_label(vacancy.created_at)}
        for vacancy in vacancies
    ]
    return render(
        request,
        "vacancies/employer_vacancy_list.html",
        {
            "vacancy_cards": vacancy_cards,
            "status_tabs": status_tabs,
            "active_status": status_filter,
        },
    )


@login_required
@role_required("employer")
def employer_vacancy_create(request):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    if request.method == "POST":
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.employer = employer_profile
            vacancy.save()
            VacancySkill.objects.bulk_create(
                [
                    VacancySkill(
                        vacancy=vacancy,
                        skill=config["skill"],
                        required_level=config["required_level"],
                        weight=1,
                        is_critical=config["is_critical"],
                    )
                    for config in form.selected_skill_configs
                ]
            )
            messages.success(request, "Вакансия успешно создана.")
            return redirect("vacancies:employer_vacancy_detail", pk=vacancy.pk)
    else:
        form = VacancyForm()
    return render(
        request,
        "vacancies/employer_vacancy_form.html",
        {
            "form": form,
            "title": "Создание вакансии",
            "submit_text": "Создать",
            "show_skill_picker": True,
        },
    )


@login_required
@role_required("employer")
def employer_vacancy_detail(request, pk):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    vacancy = _get_owned_vacancy_or_404(pk, employer_profile)
    required_skills = VacancySkill.objects.filter(vacancy=vacancy).select_related(
        "skill"
    )
    applications_count = Application.objects.filter(vacancy=vacancy).count()
    return render(
        request,
        "vacancies/employer_vacancy_detail.html",
        {
            "vacancy": vacancy,
            "required_skills": required_skills,
            "applications_count": applications_count,
            "requirement_items": _split_requirement_items(vacancy.requirements_text),
        },
    )


@login_required
@role_required("employer")
def employer_vacancy_edit(request, pk):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    vacancy = _get_owned_vacancy_or_404(pk, employer_profile)
    if request.method == "POST":
        form = VacancyForm(request.POST, instance=vacancy)
        if form.is_valid():
            form.save()
            messages.success(request, "Вакансия успешно обновлена.")
            return redirect("vacancies:employer_vacancy_detail", pk=vacancy.pk)
    else:
        form = VacancyForm(instance=vacancy)
    return render(
        request,
        "vacancies/employer_vacancy_form.html",
        {
            "form": form,
            "title": "Редактирование вакансии",
            "submit_text": "Сохранить",
            "vacancy": vacancy,
            "show_skill_picker": False,
        },
    )


@login_required
@role_required("employer")
def employer_vacancy_close(request, pk):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    vacancy = _get_owned_vacancy_or_404(pk, employer_profile)
    if request.method == "POST":
        vacancy.status = Vacancy.Status.CLOSED
        vacancy.save(update_fields=["status", "updated_at"])
        messages.success(request, "Вакансия закрыта.")
        return redirect("vacancies:employer_vacancy_detail", pk=vacancy.pk)
    return render(
        request, "vacancies/employer_vacancy_close_confirm.html", {"vacancy": vacancy}
    )


@login_required
@role_required("employer")
def employer_vacancy_publish(request, pk):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    vacancy = _get_owned_vacancy_or_404(pk, employer_profile)
    if request.method == "POST":
        vacancy.status = Vacancy.Status.PUBLISHED
        vacancy.save(update_fields=["status", "updated_at"])
        messages.success(request, "Вакансия опубликована.")
        return redirect("vacancies:employer_vacancy_detail", pk=vacancy.pk)
    return render(
        request, "vacancies/employer_vacancy_publish_confirm.html", {"vacancy": vacancy}
    )


@login_required
@role_required("employer")
def employer_vacancy_archive(request, pk):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    vacancy = _get_owned_vacancy_or_404(pk, employer_profile)
    if request.method == "POST":
        vacancy.status = Vacancy.Status.ARCHIVED
        vacancy.save(update_fields=["status", "updated_at"])
        messages.success(request, "Вакансия отправлена в архив.")
        return redirect("vacancies:employer_vacancy_detail", pk=vacancy.pk)
    return render(
        request, "vacancies/employer_vacancy_archive_confirm.html", {"vacancy": vacancy}
    )


@login_required
@role_required("employer")
def employer_vacancy_skill_create(request, vacancy_pk):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    vacancy = _get_owned_vacancy_or_404(vacancy_pk, employer_profile)
    if request.method == "POST":
        form = VacancySkillForm(request.POST, vacancy=vacancy)
        if form.is_valid():
            vacancy_skill = form.save(commit=False)
            vacancy_skill.vacancy = vacancy
            vacancy_skill.save()
            messages.success(request, "Требуемый навык успешно добавлен.")
            return redirect("vacancies:employer_vacancy_detail", pk=vacancy.pk)
    else:
        form = VacancySkillForm(vacancy=vacancy)
    return render(
        request,
        "vacancies/employer_vacancy_skill_form.html",
        {
            "form": form,
            "vacancy": vacancy,
            "title": "Добавить требуемый навык",
            "submit_text": "Добавить",
        },
    )


@login_required
@role_required("employer")
def employer_vacancy_skill_edit(request, vacancy_pk, skill_pk):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    vacancy = _get_owned_vacancy_or_404(vacancy_pk, employer_profile)
    vacancy_skill = get_object_or_404(
        VacancySkill.objects.select_related("skill"), pk=skill_pk, vacancy=vacancy
    )
    if request.method == "POST":
        form = VacancySkillForm(request.POST, instance=vacancy_skill, vacancy=vacancy)
        if form.is_valid():
            form.save()
            messages.success(request, "Требуемый навык успешно обновлен.")
            return redirect("vacancies:employer_vacancy_detail", pk=vacancy.pk)
    else:
        form = VacancySkillForm(instance=vacancy_skill, vacancy=vacancy)
    return render(
        request,
        "vacancies/employer_vacancy_skill_form.html",
        {
            "form": form,
            "vacancy": vacancy,
            "title": "Редактировать требуемый навык",
            "submit_text": "Сохранить",
        },
    )


@login_required
@role_required("employer")
def employer_vacancy_skill_delete(request, vacancy_pk, skill_pk):
    employer_profile, redirect_response = _get_employer_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    vacancy = _get_owned_vacancy_or_404(vacancy_pk, employer_profile)
    vacancy_skill = get_object_or_404(
        VacancySkill.objects.select_related("skill"), pk=skill_pk, vacancy=vacancy
    )
    if request.method == "POST":
        vacancy_skill.delete()
        messages.success(request, "Требуемый навык успешно удален.")
        return redirect("vacancies:employer_vacancy_detail", pk=vacancy.pk)
    return render(
        request,
        "vacancies/employer_vacancy_skill_confirm_delete.html",
        {"vacancy": vacancy, "vacancy_skill": vacancy_skill},
    )
