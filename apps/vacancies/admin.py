from django.contrib import admin
from .models import FavoriteVacancy, Vacancy, VacancySkill


class VacancySkillInline(admin.TabularInline):
    model = VacancySkill
    extra = 1


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "employer", "status", "internship_type", "created_at")
    list_filter = ("status", "internship_type")
    search_fields = ("title", "employer__company_name")
    inlines = [VacancySkillInline]


@admin.register(VacancySkill)
class VacancySkillAdmin(admin.ModelAdmin):
    list_display = ("vacancy", "skill", "required_level", "weight", "is_critical")
    list_filter = ("is_critical", "required_level")


@admin.register(FavoriteVacancy)
class FavoriteVacancyAdmin(admin.ModelAdmin):
    list_display = ("student_profile", "vacancy", "created_at")
    list_filter = ("created_at",)
    search_fields = ("student_profile__full_name", "vacancy__title")
