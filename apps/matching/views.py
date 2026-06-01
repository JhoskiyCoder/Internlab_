from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from apps.profiles.models import StudentProfile
from apps.users.permissions import role_required
from .services import (
    compute_next_skill_recommendations,
    compute_skill_wheel,
    get_recommended_vacancies,
)


@login_required
@role_required("student")
def student_recommendations(request):
    profile = StudentProfile.objects.filter(user=request.user).first()
    if not profile:
        messages.info(request, "Сначала заполните профиль студента.")
        return redirect("profiles:student_profile_create")
    recommendations = get_recommended_vacancies(profile)[:5]
    best_recommendation = recommendations[0] if recommendations else None
    other_recommendations = recommendations[1:] if len(recommendations) > 1 else []
    skill_wheel_categories = compute_skill_wheel(profile)
    next_skills = compute_next_skill_recommendations(profile, limit=4)
    return render(
        request,
        "matching/student_recommendations.html",
        {
            "recommendations": recommendations,
            "best_recommendation": best_recommendation,
            "other_recommendations": other_recommendations,
            "skill_wheel_categories": skill_wheel_categories,
            "next_skills": next_skills,
        },
    )


@login_required
@role_required("student")
def skill_wheel_api(request):
    profile = StudentProfile.objects.filter(user=request.user).first()
    categories = compute_skill_wheel(profile) if profile else []
    return JsonResponse({"categories": categories})
