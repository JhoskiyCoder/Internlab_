from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import UserRegistrationForm


class AuthFlowTests(TestCase):
    def test_registration_creates_user_logs_in_and_redirects_student(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "email": "student1@example.com",
                "role": "student",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(email="student1@example.com").exists())
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.redirect_chain[-1][0], reverse("profiles:student_profile_create"))

    def test_registration_redirects_employer_to_employer_profile(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "email": "employer2@example.com",
                "role": "employer",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.redirect_chain[-1][0], reverse("users:employer_dashboard"))

    def test_registration_form_role_choices_exclude_admin(self):
        form = UserRegistrationForm()
        roles = {value for value, _ in form.fields["role"].choices}
        self.assertEqual(roles, {"student", "employer"})

    def test_login_works_for_existing_user_and_redirects_by_role(self):
        user = get_user_model().objects.create_user(
            email="employer1@example.com",
            password="StrongPass123!",
            role="employer",
        )

        response = self.client.post(
            reverse("users:login"),
            {"username": user.email, "password": "StrongPass123!"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.redirect_chain[-1][0], reverse("users:employer_dashboard"))


class RoleAccessTests(TestCase):
    def setUp(self):
        self.student = get_user_model().objects.create_user(
            email="student@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.employer = get_user_model().objects.create_user(
            email="employer@example.com",
            password="StrongPass123!",
            role="employer",
        )

    def test_student_dashboard_denies_employer(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse("users:student_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_employer_dashboard_denies_student(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("users:employer_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_student_dashboard_allows_student(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("users:student_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_employer_dashboard_allows_employer(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse("users:employer_dashboard"))
        self.assertEqual(response.status_code, 200)
