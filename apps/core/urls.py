from django.urls import path

from .views import about_project, contacts, faq, home

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("about/", about_project, name="about_project"),
    path("faq/", faq, name="faq"),
    path("contacts/", contacts, name="contacts"),
]
