from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import EmployerProfile, StudentProfile


class StudentProfileFlowTests(TestCase):
    def setUp(self):
        self.student_1 = get_user_model().objects.create_user(
            email="student1@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.student_2 = get_user_model().objects.create_user(
            email="student2@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.employer = get_user_model().objects.create_user(
            email="employer@example.com",
            password="StrongPass123!",
            role="employer",
        )

    def test_student_can_create_own_profile(self):
        self.client.force_login(self.student_1)
        response = self.client.post(
            reverse("profiles:student_profile_create"),
            {
                "full_name": "Alice Student",
                "university": "KRSU",
                "faculty": "CS",
                "course": 3,
                "bio": "Looking for backend internship",
                "contact_info": "@alice",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        profile = StudentProfile.objects.get(user=self.student_1)
        self.assertEqual(profile.full_name, "Alice Student")

    def test_student_can_edit_only_own_profile(self):
        StudentProfile.objects.create(
            user=self.student_1,
            full_name="Student One",
            university="Uni 1",
            faculty="Math",
            course=2,
            bio="",
            contact_info="",
        )
        StudentProfile.objects.create(
            user=self.student_2,
            full_name="Student Two",
            university="Uni 2",
            faculty="Physics",
            course=4,
            bio="",
            contact_info="",
        )

        self.client.force_login(self.student_2)
        self.client.post(
            reverse("profiles:student_profile_edit"),
            {
                "full_name": "Updated Student Two",
                "university": "Uni 2",
                "faculty": "Physics",
                "course": 4,
                "bio": "Updated",
                "contact_info": "@two",
            },
        )

        self.assertEqual(
            StudentProfile.objects.get(user=self.student_1).full_name,
            "Student One",
        )
        self.assertEqual(
            StudentProfile.objects.get(user=self.student_2).full_name,
            "Updated Student Two",
        )

    def test_employer_cannot_access_student_profile_views(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse("profiles:student_profile_detail"))
        self.assertEqual(response.status_code, 403)


class EmployerProfileFlowTests(TestCase):
    def setUp(self):
        self.employer_1 = get_user_model().objects.create_user(
            email="employer1@example.com",
            password="StrongPass123!",
            role="employer",
        )
        self.employer_2 = get_user_model().objects.create_user(
            email="employer2@example.com",
            password="StrongPass123!",
            role="employer",
        )
        self.student = get_user_model().objects.create_user(
            email="student@example.com",
            password="StrongPass123!",
            role="student",
        )

    def test_employer_can_create_own_profile(self):
        self.client.force_login(self.employer_1)
        response = self.client.post(
            reverse("profiles:employer_profile_create"),
            {
                "company_name": "Tech LLC",
                "company_description": "Internships in Python development",
                "contact_email": "hr@tech.example",
                "website": "https://tech.example",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        profile = EmployerProfile.objects.get(user=self.employer_1)
        self.assertEqual(profile.company_name, "Tech LLC")

    def test_employer_can_edit_only_own_profile(self):
        EmployerProfile.objects.create(
            user=self.employer_1,
            company_name="Company One",
            company_description="Desc 1",
            contact_email="one@example.com",
            website="",
        )
        EmployerProfile.objects.create(
            user=self.employer_2,
            company_name="Company Two",
            company_description="Desc 2",
            contact_email="two@example.com",
            website="",
        )

        self.client.force_login(self.employer_2)
        self.client.post(
            reverse("profiles:employer_profile_edit"),
            {
                "company_name": "Updated Company Two",
                "company_description": "Desc 2",
                "contact_email": "two@example.com",
                "website": "",
            },
        )

        self.assertEqual(
            EmployerProfile.objects.get(user=self.employer_1).company_name,
            "Company One",
        )
        self.assertEqual(
            EmployerProfile.objects.get(user=self.employer_2).company_name,
            "Updated Company Two",
        )

    def test_student_cannot_access_employer_profile_views(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("profiles:employer_profile_detail"))
        self.assertEqual(response.status_code, 403)
