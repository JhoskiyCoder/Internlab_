from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    full_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to="avatars/students/", blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True)
    university = models.CharField(max_length=255)
    faculty = models.CharField(max_length=255)
    course = models.PositiveSmallIntegerField()
    bio = models.TextField(blank=True)
    languages = models.TextField(blank=True, default="")
    contact_info = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("full_name",)

    def __str__(self):
        return self.full_name


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_profile",
    )
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="avatars/employers/", blank=True, null=True)
    company_description = models.TextField()
    contact_email = models.EmailField()
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("company_name",)

    def __str__(self):
        return self.company_name


class StudentProject(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-start_date")

    def __str__(self):
        return f"{self.student_profile.full_name}: {self.title}"
