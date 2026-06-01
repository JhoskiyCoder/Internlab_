from django.contrib import admin

from .models import Skill, StudentSkill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name", "category")


@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ("student_profile", "skill", "level")
    list_filter = ("level",)
    search_fields = ("student_profile__full_name", "skill__name")
