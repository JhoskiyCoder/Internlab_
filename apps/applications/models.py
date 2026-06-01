from django.db import models


class Application(models.Model):

    class Status(models.TextChoices):
        SUBMITTED = ("submitted", "Подана")
        REVIEWING = ("reviewing", "На рассмотрении")
        ACCEPTED = ("accepted", "Принята")
        REJECTED = ("rejected", "Отклонена")

    student = models.ForeignKey(
        "profiles.StudentProfile", on_delete=models.CASCADE, related_name="applications"
    )
    vacancy = models.ForeignKey(
        "vacancies.Vacancy", on_delete=models.CASCADE, related_name="applications"
    )
    cover_letter = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SUBMITTED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "vacancy")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.student.full_name} -> {self.vacancy.title} ({self.status})"
