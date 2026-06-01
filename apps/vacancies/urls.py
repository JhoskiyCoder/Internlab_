from django.urls import path

from .views import (
    employer_vacancy_archive,
    employer_vacancy_close,
    employer_vacancy_create,
    employer_vacancy_detail,
    employer_vacancy_edit,
    employer_vacancy_list,
    employer_vacancy_publish,
    employer_vacancy_skill_create,
    employer_vacancy_skill_delete,
    employer_vacancy_skill_edit,
    student_favorite_vacancy_list,
    toggle_favorite_vacancy,
    vacancy_public_detail,
    vacancy_public_list,
)

app_name = "vacancies"

urlpatterns = [
    path("", vacancy_public_list, name="public_list"),
    path("favorites/", student_favorite_vacancy_list, name="student_favorites"),
    path("<int:pk>/", vacancy_public_detail, name="public_detail"),
    path("favorites/<int:pk>/toggle/", toggle_favorite_vacancy, name="toggle_favorite"),
    path("employer/", employer_vacancy_list, name="employer_list"),
    path("employer/create/", employer_vacancy_create, name="employer_create"),
    path("employer/<int:pk>/", employer_vacancy_detail, name="employer_vacancy_detail"),
    path("employer/<int:pk>/edit/", employer_vacancy_edit, name="employer_edit"),
    path("employer/<int:pk>/publish/", employer_vacancy_publish, name="employer_publish"),
    path("employer/<int:pk>/close/", employer_vacancy_close, name="employer_close"),
    path("employer/<int:pk>/archive/", employer_vacancy_archive, name="employer_archive"),
    path(
        "employer/<int:vacancy_pk>/skills/add/",
        employer_vacancy_skill_create,
        name="skill_add",
    ),
    path(
        "employer/<int:vacancy_pk>/skills/<int:skill_pk>/edit/",
        employer_vacancy_skill_edit,
        name="skill_edit",
    ),
    path(
        "employer/<int:vacancy_pk>/skills/<int:skill_pk>/delete/",
        employer_vacancy_skill_delete,
        name="skill_delete",
    ),
]
