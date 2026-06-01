from django.urls import path

from .views import (
    applications_home,
    employer_application_detail,
    employer_application_list,
    student_application_create,
    student_application_list,
)

app_name = "applications"

urlpatterns = [
    path("", applications_home, name="home"),
    path("student/", student_application_list, name="student_list"),
    path("vacancy/<int:vacancy_pk>/apply/", student_application_create, name="student_apply"),
    path("employer/", employer_application_list, name="employer_list"),
    path("employer/<int:pk>/", employer_application_detail, name="employer_detail"),
]
