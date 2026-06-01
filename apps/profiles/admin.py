from django.contrib import admin
from .models import EmployerProfile, StudentProfile, StudentProject


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "university", "faculty", "course", "user")
    search_fields = ("full_name", "university", "faculty", "user__email")


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_email", "user")
    search_fields = ("company_name", "contact_email", "user__email")


@admin.register(StudentProject)
class StudentProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "student_profile",
        "role",
        "start_date",
        "end_date",
        "is_current",
    )
    search_fields = (
        "title",
        "role",
        "student_profile__full_name",
        "student_profile__user__email",
    )
    list_filter = ("is_current",)
