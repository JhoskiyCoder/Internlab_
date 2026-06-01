from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from apps.profiles.models import StudentProfile
from apps.users.permissions import role_required
from .forms import StudentSkillForm
from .models import StudentSkill


def _get_student_profile_or_redirect(request):
    profile = StudentProfile.objects.filter(user=request.user).first()
    if not profile:
        messages.info(request, "Сначала заполните профиль студента.")
        return (None, redirect("profiles:student_profile_create"))
    return (profile, None)


@login_required
@role_required("student")
def student_skill_list(request):
    profile, redirect_response = _get_student_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    skills = (
        StudentSkill.objects.filter(student_profile=profile)
        .select_related("skill")
        .order_by("skill__category", "skill__name")
    )
    skills_count = skills.count()
    avg_level = (
        round(sum((item.level for item in skills)) / skills_count, 1)
        if skills_count
        else 0
    )
    return render(
        request,
        "skills/student_skill_list.html",
        {"skills": skills, "skills_count": skills_count, "avg_level": avg_level},
    )


@login_required
@role_required("student")
def student_skill_create(request):
    profile, redirect_response = _get_student_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    if request.method == "POST":
        form = StudentSkillForm(request.POST, student_profile=profile)
        if form.is_valid():
            student_skill = form.save(commit=False)
            student_skill.student_profile = profile
            student_skill.save()
            messages.success(request, "Навык успешно добавлен.")
            return redirect("skills:student_skill_list")
    else:
        form = StudentSkillForm(student_profile=profile)
    return render(
        request,
        "skills/student_skill_form.html",
        {"form": form, "title": "Добавить навык", "submit_text": "Добавить"},
    )


@login_required
@role_required("student")
def student_skill_edit(request, pk):
    profile, redirect_response = _get_student_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    student_skill = get_object_or_404(StudentSkill, pk=pk, student_profile=profile)
    if request.method == "POST":
        form = StudentSkillForm(
            request.POST, instance=student_skill, student_profile=profile
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Навык успешно обновлен.")
            return redirect("skills:student_skill_list")
    else:
        form = StudentSkillForm(instance=student_skill, student_profile=profile)
    return render(
        request,
        "skills/student_skill_form.html",
        {"form": form, "title": "Редактировать навык", "submit_text": "Сохранить"},
    )


@login_required
@role_required("student")
def student_skill_delete(request, pk):
    profile, redirect_response = _get_student_profile_or_redirect(request)
    if redirect_response:
        return redirect_response
    student_skill = get_object_or_404(StudentSkill, pk=pk, student_profile=profile)
    if request.method == "POST":
        student_skill.delete()
        messages.success(request, "Навык успешно удален.")
        return redirect("skills:student_skill_list")
    return render(
        request,
        "skills/student_skill_confirm_delete.html",
        {"student_skill": student_skill},
    )
