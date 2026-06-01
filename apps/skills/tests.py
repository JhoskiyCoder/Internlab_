from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.profiles.models import StudentProfile

from .models import Skill, StudentSkill


class StudentSkillFlowTests(TestCase):
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

        self.profile_1 = StudentProfile.objects.create(
            user=self.student_1,
            full_name="Student One",
            university="KRSU",
            faculty="CS",
            course=3,
            bio="",
            contact_info="",
        )
        self.profile_2 = StudentProfile.objects.create(
            user=self.student_2,
            full_name="Student Two",
            university="KRSU",
            faculty="CS",
            course=4,
            bio="",
            contact_info="",
        )

        self.python_skill = Skill.objects.create(name="Python", category="Programming")
        self.sql_skill = Skill.objects.create(name="SQL", category="Databases")

    def test_student_can_add_skill(self):
        self.client.force_login(self.student_1)
        response = self.client.post(
            reverse("skills:student_skill_add"),
            {"skill": self.python_skill.pk, "level": 4},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            StudentSkill.objects.filter(
                student_profile=self.profile_1,
                skill=self.python_skill,
                level=4,
            ).exists()
        )

    def test_student_cannot_add_duplicate_skill(self):
        StudentSkill.objects.create(student_profile=self.profile_1, skill=self.python_skill, level=3)

        self.client.force_login(self.student_1)
        response = self.client.post(
            reverse("skills:student_skill_add"),
            {"skill": self.python_skill.pk, "level": 5},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже добавлен")
        self.assertEqual(
            StudentSkill.objects.filter(student_profile=self.profile_1, skill=self.python_skill).count(),
            1,
        )

    def test_student_can_edit_own_skill(self):
        student_skill = StudentSkill.objects.create(student_profile=self.profile_1, skill=self.python_skill, level=2)

        self.client.force_login(self.student_1)
        self.client.post(
            reverse("skills:student_skill_edit", args=[student_skill.pk]),
            {"skill": self.python_skill.pk, "level": 5},
            follow=True,
        )

        student_skill.refresh_from_db()
        self.assertEqual(student_skill.level, 5)

    def test_student_can_delete_own_skill(self):
        student_skill = StudentSkill.objects.create(student_profile=self.profile_1, skill=self.python_skill, level=2)

        self.client.force_login(self.student_1)
        self.client.post(reverse("skills:student_skill_delete", args=[student_skill.pk]), follow=True)

        self.assertFalse(StudentSkill.objects.filter(pk=student_skill.pk).exists())

    def test_student_cannot_edit_other_students_skill(self):
        student_skill = StudentSkill.objects.create(student_profile=self.profile_1, skill=self.python_skill, level=2)

        self.client.force_login(self.student_2)
        response = self.client.get(reverse("skills:student_skill_edit", args=[student_skill.pk]))

        self.assertEqual(response.status_code, 404)

    def test_employer_cannot_access_student_skills_page(self):
        self.client.force_login(self.employer)
        response = self.client.get(reverse("skills:student_skill_list"))

        self.assertEqual(response.status_code, 403)
