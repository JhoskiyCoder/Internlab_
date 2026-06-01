from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Skill(models.Model):
    class Category(models.TextChoices):
        BACKEND = "Backend", "Бэкенд"
        FRONTEND = "Frontend", "Фронтенд"
        DEVOPS = "DevOps", "DevOps"
        DATA_SCIENCE = "Data Science", "Аналитика данных"
        MACHINE_LEARNING = "Machine Learning", "Машинное обучение"
        CORE_SKILLS = "Core Skills", "Базовые навыки"
        MOBILE = "Mobile", "Мобильная разработка"

    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.BACKEND,
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class StudentSkill(models.Model):
    student_profile = models.ForeignKey("profiles.StudentProfile", on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="student_entries")
    level = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ("student_profile", "skill")
        ordering = ("student_profile", "skill")

    def __str__(self):
        return f"{self.student_profile.full_name}: {self.skill.name} ({self.level})"
