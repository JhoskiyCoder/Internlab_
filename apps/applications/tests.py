from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.profiles.models import EmployerProfile, StudentProfile
from apps.vacancies.models import Vacancy

from .models import Application


class StudentApplicationFlowTests(TestCase):
    def setUp(self):
        self.student_user = get_user_model().objects.create_user(
            email="student@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            full_name="Student",
            university="KRSU",
            faculty="CS",
            course=3,
            bio="",
            contact_info="",
        )

        employer_user = get_user_model().objects.create_user(
            email="employer@example.com",
            password="StrongPass123!",
            role="employer",
        )
        self.employer_profile = EmployerProfile.objects.create(
            user=employer_user,
            company_name="Tech LLC",
            company_description="desc",
            contact_email="hr@tech.example",
            website="",
        )

        self.published_vacancy = Vacancy.objects.create(
            employer=self.employer_profile,
            title="Backend Intern",
            description="desc",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.PUBLISHED,
        )
        self.closed_vacancy = Vacancy.objects.create(
            employer=self.employer_profile,
            title="Closed Intern",
            description="desc",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.CLOSED,
        )
        self.archived_vacancy = Vacancy.objects.create(
            employer=self.employer_profile,
            title="Archived Intern",
            description="desc",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.ARCHIVED,
        )

    def test_student_can_apply_to_published_vacancy(self):
        self.client.force_login(self.student_user)
        response = self.client.post(
            reverse("applications:student_apply", args=[self.published_vacancy.pk]),
            {"cover_letter": "I have Python and Django experience."},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Application.objects.filter(
                student=self.student_profile,
                vacancy=self.published_vacancy,
                status=Application.Status.SUBMITTED,
            ).exists()
        )

    def test_student_cannot_apply_twice(self):
        Application.objects.create(student=self.student_profile, vacancy=self.published_vacancy, cover_letter="First")

        self.client.force_login(self.student_user)
        self.client.post(
            reverse("applications:student_apply", args=[self.published_vacancy.pk]),
            {"cover_letter": "Second"},
            follow=True,
        )

        self.assertEqual(
            Application.objects.filter(student=self.student_profile, vacancy=self.published_vacancy).count(),
            1,
        )

    def test_closed_or_archived_vacancies_reject_applications(self):
        self.client.force_login(self.student_user)

        closed_response = self.client.post(
            reverse("applications:student_apply", args=[self.closed_vacancy.pk]),
            {"cover_letter": "Attempt closed"},
            follow=True,
        )
        archived_response = self.client.post(
            reverse("applications:student_apply", args=[self.archived_vacancy.pk]),
            {"cover_letter": "Attempt archived"},
            follow=True,
        )

        self.assertEqual(closed_response.status_code, 404)
        self.assertEqual(archived_response.status_code, 404)
        self.assertFalse(Application.objects.filter(vacancy=self.closed_vacancy).exists())
        self.assertFalse(Application.objects.filter(vacancy=self.archived_vacancy).exists())


class EmployerApplicationFlowTests(TestCase):
    def setUp(self):
        self.student_user = get_user_model().objects.create_user(
            email="student2@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            full_name="Student Two",
            university="KRSU",
            faculty="CS",
            course=2,
            bio="",
            contact_info="",
        )

        self.employer_user_1 = get_user_model().objects.create_user(
            email="emp1@example.com",
            password="StrongPass123!",
            role="employer",
        )
        self.employer_profile_1 = EmployerProfile.objects.create(
            user=self.employer_user_1,
            company_name="Company One",
            company_description="desc",
            contact_email="one@example.com",
            website="",
        )

        self.employer_user_2 = get_user_model().objects.create_user(
            email="emp2@example.com",
            password="StrongPass123!",
            role="employer",
        )
        self.employer_profile_2 = EmployerProfile.objects.create(
            user=self.employer_user_2,
            company_name="Company Two",
            company_description="desc",
            contact_email="two@example.com",
            website="",
        )

        self.vacancy_1 = Vacancy.objects.create(
            employer=self.employer_profile_1,
            title="Role One",
            description="desc",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.PUBLISHED,
        )
        self.vacancy_2 = Vacancy.objects.create(
            employer=self.employer_profile_2,
            title="Role Two",
            description="desc",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.PUBLISHED,
        )

        self.app_own = Application.objects.create(student=self.student_profile, vacancy=self.vacancy_1, cover_letter="hello")
        self.app_other = Application.objects.create(student=self.student_profile, vacancy=self.vacancy_2, cover_letter="hello")

    def test_employer_sees_only_own_vacancy_applications(self):
        self.client.force_login(self.employer_user_1)
        response = self.client.get(reverse("applications:employer_list"))

        self.assertContains(response, "Role One")
        self.assertNotContains(response, "Role Two")

    def test_employer_can_change_status_for_own_application(self):
        self.client.force_login(self.employer_user_1)
        self.client.post(
            reverse("applications:employer_detail", args=[self.app_own.pk]),
            {"status": Application.Status.ACCEPTED},
            follow=True,
        )

        self.app_own.refresh_from_db()
        self.assertEqual(self.app_own.status, Application.Status.ACCEPTED)

    def test_employer_cannot_change_status_for_other_employer_application(self):
        self.client.force_login(self.employer_user_1)
        response = self.client.post(
            reverse("applications:employer_detail", args=[self.app_other.pk]),
            {"status": Application.Status.REJECTED},
        )

        self.assertEqual(response.status_code, 404)
