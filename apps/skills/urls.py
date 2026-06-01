from django.urls import path

from .views import (
    student_skill_create,
    student_skill_delete,
    student_skill_edit,
    student_skill_list,
)

app_name = "skills"

urlpatterns = [
    path("student/", student_skill_list, name="student_skill_list"),
    path("student/add/", student_skill_create, name="student_skill_add"),
    path("student/<int:pk>/edit/", student_skill_edit, name="student_skill_edit"),
    path("student/<int:pk>/delete/", student_skill_delete, name="student_skill_delete"),
]
