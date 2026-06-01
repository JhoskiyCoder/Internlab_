from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Vacancy(models.Model):

    class Status(models.TextChoices):
        DRAFT = ("draft", "Черновик")
        PUBLISHED = ("published", "Опубликована")
        CLOSED = ("closed", "Закрыта")
        ARCHIVED = ("archived", "В архиве")

    class InternshipType(models.TextChoices):
        ONSITE = ("onsite", "Офис")
        REMOTE = ("remote", "Удаленно")
        HYBRID = ("hybrid", "Гибрид")

    employer = models.ForeignKey(
        "profiles.EmployerProfile", on_delete=models.CASCADE, related_name="vacancies"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements_text = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    internship_type = models.CharField(
        max_length=20, choices=InternshipType.choices, default=InternshipType.ONSITE
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    @property
    def display_location(self):
        if not self.location:
            return "Не указано"
        location = self.location.strip()
        if location.lower() in {"гибрид", "удаленно", "hybrid", "remote"}:
            return "Не указано"
        return location


class VacancySkill(models.Model):
    vacancy = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name="required_skills"
    )
    skill = models.ForeignKey(
        "skills.Skill", on_delete=models.CASCADE, related_name="vacancy_requirements"
    )
    required_level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    weight = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    is_critical = models.BooleanField(default=False)

    class Meta:
        unique_together = ("vacancy", "skill")
        ordering = ("vacancy", "skill")

    def __str__(self):
        return f"{self.vacancy.title}: {self.skill.name}"


class FavoriteVacancy(models.Model):
    student_profile = models.ForeignKey(
        "profiles.StudentProfile",
        on_delete=models.CASCADE,
        related_name="favorite_vacancies",
    )
    vacancy = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name="favorited_by_students"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student_profile", "vacancy")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.student_profile.full_name}: {self.vacancy.title}"
