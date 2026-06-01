from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from apps.matching.views import skill_wheel_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("", include("apps.users.urls")),
    path("profiles/", include("apps.profiles.urls")),
    path("skills/", include("apps.skills.urls")),
    path("vacancies/", include("apps.vacancies.urls")),
    path("applications/", include("apps.applications.urls")),
    path("matching/", include("apps.matching.urls")),
    path("api/skill-wheel/", skill_wheel_api),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
