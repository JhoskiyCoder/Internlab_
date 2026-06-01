from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.profiles.models import EmployerProfile, StudentProfile
from apps.skills.models import Skill

from .models import FavoriteVacancy, Vacancy, VacancySkill


class EmployerVacancyFlowTests(TestCase):
    def setUp(self):
        self.employer_user_1 = get_user_model().objects.create_user(
            email="emp1@example.com",
            password="StrongPass123!",
            role="employer",
        )
        self.employer_user_2 = get_user_model().objects.create_user(
            email="emp2@example.com",
            password="StrongPass123!",
            role="employer",
        )
        self.student_user = get_user_model().objects.create_user(
            email="student@example.com",
            password="StrongPass123!",
            role="student",
        )

        self.employer_profile_1 = EmployerProfile.objects.create(
            user=self.employer_user_1,
            company_name="Company One",
            company_description="Desc",
            contact_email="one@example.com",
            website="",
        )
        self.employer_profile_2 = EmployerProfile.objects.create(
            user=self.employer_user_2,
            company_name="Company Two",
            company_description="Desc",
            contact_email="two@example.com",
            website="",
        )

        self.vacancy_1 = Vacancy.objects.create(
            employer=self.employer_profile_1,
            title="Backend Intern",
            description="Django internship",
            requirements_text="Python",
            location="Bishkek",
            internship_type=Vacancy.InternshipType.ONSITE,
            status=Vacancy.Status.DRAFT,
        )
        self.python_skill = Skill.objects.create(name="Python", category="Programming")
        self.sql_skill = Skill.objects.create(name="SQL", category="Databases")

    def test_employer_can_create_own_vacancy(self):
        self.client.force_login(self.employer_user_1)
        response = self.client.post(
            reverse("vacancies:employer_create"),
            {
                "title": "Data Intern",
                "description": "SQL and analytics",
                "requirements_text": "SQL",
                "location": "Remote",
                "internship_type": Vacancy.InternshipType.REMOTE,
                "status": Vacancy.Status.PUBLISHED,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Vacancy.objects.filter(
                employer=self.employer_profile_1,
                title="Data Intern",
                status=Vacancy.Status.PUBLISHED,
            ).exists()
        )

    def test_employer_can_only_see_own_vacancies(self):
        Vacancy.objects.create(
            employer=self.employer_profile_2,
            title="Other Vacancy",
            description="Other",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.HYBRID,
            status=Vacancy.Status.DRAFT,
        )

        self.client.force_login(self.employer_user_1)
        response = self.client.get(reverse("vacancies:employer_list"))

        self.assertContains(response, "Backend Intern")
        self.assertNotContains(response, "Other Vacancy")

    def test_employer_cannot_edit_other_employer_vacancy(self):
        other_vacancy = Vacancy.objects.create(
            employer=self.employer_profile_2,
            title="Other Vacancy",
            description="Other",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.HYBRID,
            status=Vacancy.Status.DRAFT,
        )

        self.client.force_login(self.employer_user_1)
        response = self.client.get(reverse("vacancies:employer_edit", args=[other_vacancy.pk]))

        self.assertEqual(response.status_code, 404)

    def test_employer_can_close_own_vacancy(self):
        self.client.force_login(self.employer_user_1)
        self.client.post(reverse("vacancies:employer_close", args=[self.vacancy_1.pk]), follow=True)

        self.vacancy_1.refresh_from_db()
        self.assertEqual(self.vacancy_1.status, Vacancy.Status.CLOSED)

    def test_employer_can_publish_own_vacancy(self):
        self.client.force_login(self.employer_user_1)
        self.client.post(reverse("vacancies:employer_publish", args=[self.vacancy_1.pk]), follow=True)

        self.vacancy_1.refresh_from_db()
        self.assertEqual(self.vacancy_1.status, Vacancy.Status.PUBLISHED)

    def test_employer_can_archive_own_vacancy(self):
        self.client.force_login(self.employer_user_1)
        self.client.post(reverse("vacancies:employer_archive", args=[self.vacancy_1.pk]), follow=True)

        self.vacancy_1.refresh_from_db()
        self.assertEqual(self.vacancy_1.status, Vacancy.Status.ARCHIVED)

    def test_student_cannot_access_employer_vacancy_pages(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("vacancies:employer_list"))

        self.assertEqual(response.status_code, 403)

    def test_employer_can_add_required_skill_to_own_vacancy(self):
        self.client.force_login(self.employer_user_1)
        response = self.client.post(
            reverse("vacancies:skill_add", args=[self.vacancy_1.pk]),
            {
                "skill": self.python_skill.pk,
                "required_level": 4,
                "weight": 3,
                "is_critical": True,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            VacancySkill.objects.filter(
                vacancy=self.vacancy_1,
                skill=self.python_skill,
                required_level=4,
                weight=1,
                is_critical=True,
            ).exists()
        )

    def test_employer_cannot_add_duplicate_required_skill(self):
        VacancySkill.objects.create(
            vacancy=self.vacancy_1,
            skill=self.python_skill,
            required_level=3,
            weight=2,
            is_critical=False,
        )

        self.client.force_login(self.employer_user_1)
        response = self.client.post(
            reverse("vacancies:skill_add", args=[self.vacancy_1.pk]),
            {
                "skill": self.python_skill.pk,
                "required_level": 5,
                "weight": 5,
                "is_critical": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже добавлен")
        self.assertEqual(
            VacancySkill.objects.filter(vacancy=self.vacancy_1, skill=self.python_skill).count(),
            1,
        )

    def test_employer_can_edit_and_delete_vacancy_skill(self):
        vacancy_skill = VacancySkill.objects.create(
            vacancy=self.vacancy_1,
            skill=self.python_skill,
            required_level=2,
            weight=1,
            is_critical=False,
        )

        self.client.force_login(self.employer_user_1)
        self.client.post(
            reverse("vacancies:skill_edit", args=[self.vacancy_1.pk, vacancy_skill.pk]),
            {
                "skill": self.sql_skill.pk,
                "required_level": 5,
                "weight": 4,
                "is_critical": True,
            },
            follow=True,
        )
        vacancy_skill.refresh_from_db()
        self.assertEqual(vacancy_skill.skill, self.sql_skill)
        self.assertEqual(vacancy_skill.required_level, 5)
        self.assertEqual(vacancy_skill.weight, 1)
        self.assertTrue(vacancy_skill.is_critical)

        self.client.post(
            reverse("vacancies:skill_delete", args=[self.vacancy_1.pk, vacancy_skill.pk]),
            follow=True,
        )
        self.assertFalse(VacancySkill.objects.filter(pk=vacancy_skill.pk).exists())

    def test_employer_cannot_manage_other_employer_vacancy_skills(self):
        other_vacancy = Vacancy.objects.create(
            employer=self.employer_profile_2,
            title="Other Vacancy",
            description="Other",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.DRAFT,
        )
        other_skill = VacancySkill.objects.create(
            vacancy=other_vacancy,
            skill=self.sql_skill,
            required_level=2,
            weight=2,
            is_critical=False,
        )

        self.client.force_login(self.employer_user_1)
        add_response = self.client.get(reverse("vacancies:skill_add", args=[other_vacancy.pk]))
        edit_response = self.client.get(reverse("vacancies:skill_edit", args=[other_vacancy.pk, other_skill.pk]))
        delete_response = self.client.get(reverse("vacancies:skill_delete", args=[other_vacancy.pk, other_skill.pk]))

        self.assertEqual(add_response.status_code, 404)
        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)

    def test_employer_cannot_change_status_of_other_employer_vacancy(self):
        other_vacancy = Vacancy.objects.create(
            employer=self.employer_profile_2,
            title="Other Vacancy",
            description="Other",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.DRAFT,
        )

        self.client.force_login(self.employer_user_1)
        publish_response = self.client.post(reverse("vacancies:employer_publish", args=[other_vacancy.pk]))
        archive_response = self.client.post(reverse("vacancies:employer_archive", args=[other_vacancy.pk]))
        close_response = self.client.post(reverse("vacancies:employer_close", args=[other_vacancy.pk]))

        self.assertEqual(publish_response.status_code, 404)
        self.assertEqual(archive_response.status_code, 404)
        self.assertEqual(close_response.status_code, 404)


class PublicVacancyListingTests(TestCase):
    def setUp(self):
        employer_user = get_user_model().objects.create_user(
            email="emp@example.com",
            password="StrongPass123!",
            role="employer",
        )
        employer_profile = EmployerProfile.objects.create(
            user=employer_user,
            company_name="Company",
            company_description="Desc",
            contact_email="company@example.com",
            website="",
        )
        self.published_vacancy = Vacancy.objects.create(
            employer=employer_profile,
            title="Published Vacancy",
            description="Visible",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.PUBLISHED,
        )
        self.draft_vacancy = Vacancy.objects.create(
            employer=employer_profile,
            title="Draft Vacancy",
            description="Hidden",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.DRAFT,
        )

    def test_public_list_shows_only_published(self):
        response = self.client.get(reverse("vacancies:public_list"))

        self.assertContains(response, "Published Vacancy")
        self.assertNotContains(response, "Draft Vacancy")

    def test_public_detail_available_only_for_published(self):
        published_response = self.client.get(reverse("vacancies:public_detail", args=[self.published_vacancy.pk]))
        draft_response = self.client.get(reverse("vacancies:public_detail", args=[self.draft_vacancy.pk]))

        self.assertEqual(published_response.status_code, 200)
        self.assertEqual(draft_response.status_code, 404)


class StudentFavoriteVacancyTests(TestCase):
    def setUp(self):
        self.student_user = get_user_model().objects.create_user(
            email="student-fav@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            full_name="Student Favorite",
            university="KRSU",
            faculty="CS",
            course=3,
            bio="",
            contact_info="",
        )

        self.employer_user = get_user_model().objects.create_user(
            email="employer-fav@example.com",
            password="StrongPass123!",
            role="employer",
        )
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name="Favorite Company",
            company_description="Desc",
            contact_email="favorite@example.com",
            website="",
        )

        self.vacancy = Vacancy.objects.create(
            employer=self.employer_profile,
            title="Favorite Vacancy",
            description="Desc",
            requirements_text="",
            location="Bishkek",
            internship_type=Vacancy.InternshipType.HYBRID,
            status=Vacancy.Status.PUBLISHED,
        )

    def test_student_can_toggle_favorite(self):
        self.client.force_login(self.student_user)

        add_response = self.client.post(
            reverse("vacancies:toggle_favorite", args=[self.vacancy.pk]),
            {"next": reverse("vacancies:public_list")},
            follow=True,
        )
        self.assertEqual(add_response.status_code, 200)
        self.assertTrue(
            FavoriteVacancy.objects.filter(student_profile=self.student_profile, vacancy=self.vacancy).exists()
        )

        remove_response = self.client.post(
            reverse("vacancies:toggle_favorite", args=[self.vacancy.pk]),
            {"next": reverse("vacancies:public_list")},
            follow=True,
        )
        self.assertEqual(remove_response.status_code, 200)
        self.assertFalse(
            FavoriteVacancy.objects.filter(student_profile=self.student_profile, vacancy=self.vacancy).exists()
        )

    def test_student_can_view_favorite_vacancies_page(self):
        FavoriteVacancy.objects.create(student_profile=self.student_profile, vacancy=self.vacancy)
        self.client.force_login(self.student_user)

        response = self.client.get(reverse("vacancies:student_favorites"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Избранные вакансии")
        self.assertContains(response, "Favorite Vacancy")

    def test_empty_favorites_page_has_empty_message(self):
        self.client.force_login(self.student_user)

        response = self.client.get(reverse("vacancies:student_favorites"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "В избранном пока нет вакансий")

    def test_employer_cannot_view_student_favorites_page(self):
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("vacancies:student_favorites"))
        self.assertEqual(response.status_code, 403)

    def test_employer_cannot_toggle_favorite(self):
        self.client.force_login(self.employer_user)
        response = self.client.post(reverse("vacancies:toggle_favorite", args=[self.vacancy.pk]))
        self.assertEqual(response.status_code, 403)
