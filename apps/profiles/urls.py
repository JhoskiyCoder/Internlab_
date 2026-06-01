from django.urls import path

from .views import (
    employer_profile_create,
    employer_profile_detail,
    employer_profile_edit,
    student_profile_create,
    student_profile_detail,
    student_profile_edit,
)

app_name = "profiles"

urlpatterns = [
    path("student/", student_profile_detail, name="student_profile_detail"),
    path("student/create/", student_profile_create, name="student_profile_create"),
    path("student/edit/", student_profile_edit, name="student_profile_edit"),
    path("employer/", employer_profile_detail, name="employer_profile_detail"),
    path("employer/create/", employer_profile_create, name="employer_profile_create"),
    path("employer/edit/", employer_profile_edit, name="employer_profile_edit"),
]
