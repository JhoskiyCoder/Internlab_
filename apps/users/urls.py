from django.contrib.auth import views as auth_views
from django.urls import path

from .views import RegisterView, RoleLoginView, employer_dashboard, student_dashboard

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", RoleLoginView.as_view(), name="login"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="registration/logged_out.html"),
        name="logout",
    ),
    path("student/dashboard/", student_dashboard, name="student_dashboard"),
    path("employer/dashboard/", employer_dashboard, name="employer_dashboard"),
]
