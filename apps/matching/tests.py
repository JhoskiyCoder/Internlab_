from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.profiles.models import EmployerProfile, StudentProfile
from apps.skills.models import Skill, StudentSkill
from apps.vacancies.models import Vacancy, VacancySkill

from .services import (
    calculate_vacancy_match,
    compute_next_skill_recommendations,
    compute_skill_wheel,
    get_recommended_vacancies,
)


class MatchingServiceTests(TestCase):
    def setUp(self):
        self.student_user = get_user_model().objects.create_user(
            email="student@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            full_name="Student One",
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
            company_description="Internships",
            contact_email="hr@tech.example",
            website="",
        )

        self.python = Skill.objects.create(name="Python", category="Programming")
        self.sql = Skill.objects.create(name="SQL", category="Databases")
        self.git = Skill.objects.create(name="Git", category="Tools")

    def _create_published_vacancy(self, title):
        return Vacancy.objects.create(
            employer=self.employer_profile,
            title=title,
            description="desc",
            requirements_text="",
            location="Bishkek",
            internship_type=Vacancy.InternshipType.HYBRID,
            status=Vacancy.Status.PUBLISHED,
        )

    def test_exact_match_returns_100(self):
        vacancy = self._create_published_vacancy("Exact")
        VacancySkill.objects.create(vacancy=vacancy, skill=self.python, required_level=3, weight=2, is_critical=False)
        VacancySkill.objects.create(vacancy=vacancy, skill=self.sql, required_level=2, weight=1, is_critical=False)

        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.python, level=3)
        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.sql, level=2)

        result = calculate_vacancy_match(self.student_profile, vacancy)
        self.assertEqual(result.score, 100.0)
        self.assertEqual(result.missing_skills, [])
        self.assertFalse(result.missing_critical_skills)

    def test_partial_match(self):
        vacancy = self._create_published_vacancy("Partial")
        VacancySkill.objects.create(vacancy=vacancy, skill=self.python, required_level=4, weight=2, is_critical=False)
        VacancySkill.objects.create(vacancy=vacancy, skill=self.sql, required_level=2, weight=2, is_critical=False)

        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.python, level=2)
        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.sql, level=2)

        result = calculate_vacancy_match(self.student_profile, vacancy)
        self.assertEqual(result.score, 75.0)

    def test_no_matching_skills(self):
        vacancy = self._create_published_vacancy("No Match")
        VacancySkill.objects.create(vacancy=vacancy, skill=self.python, required_level=3, weight=1, is_critical=False)

        result = calculate_vacancy_match(self.student_profile, vacancy)
        self.assertEqual(result.score, 0.0)
        self.assertEqual(result.missing_skills, ["Python"])

    def test_missing_critical_skill_reduces_score(self):
        vacancy = self._create_published_vacancy("Critical")
        VacancySkill.objects.create(vacancy=vacancy, skill=self.python, required_level=2, weight=1, is_critical=True)
        VacancySkill.objects.create(vacancy=vacancy, skill=self.sql, required_level=2, weight=1, is_critical=False)

        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.sql, level=2)

        result = calculate_vacancy_match(self.student_profile, vacancy)
        self.assertEqual(result.score, 40.0)
        self.assertTrue(result.missing_critical_skills)
        self.assertIn("Python", result.missing_skills)

    def test_vacancy_with_no_required_skills(self):
        vacancy = self._create_published_vacancy("No Requirements")
        result = calculate_vacancy_match(self.student_profile, vacancy)

        self.assertEqual(result.score, 100.0)
        self.assertEqual(result.missing_skills, [])
        self.assertFalse(result.missing_critical_skills)

    def test_student_with_no_skills(self):
        vacancy = self._create_published_vacancy("No Student Skills")
        VacancySkill.objects.create(vacancy=vacancy, skill=self.git, required_level=3, weight=2, is_critical=False)

        result = calculate_vacancy_match(self.student_profile, vacancy)
        self.assertEqual(result.score, 0.0)
        self.assertEqual(result.missing_skills, ["Git"])

    def test_recommendations_sorted_descending(self):
        high = self._create_published_vacancy("High")
        low = self._create_published_vacancy("Low")

        VacancySkill.objects.create(vacancy=high, skill=self.python, required_level=2, weight=1, is_critical=False)
        VacancySkill.objects.create(vacancy=low, skill=self.sql, required_level=5, weight=1, is_critical=False)

        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.python, level=3)
        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.sql, level=1)

        results = get_recommended_vacancies(self.student_profile)
        self.assertGreaterEqual(results[0].score, results[1].score)
        self.assertEqual(results[0].vacancy.title, "High")


class RecommendationPageTests(TestCase):
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

        self.employer_user = get_user_model().objects.create_user(
            email="emp2@example.com",
            password="StrongPass123!",
            role="employer",
        )
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name="Biz",
            company_description="desc",
            contact_email="hr@biz.example",
            website="",
        )

        self.skill = Skill.objects.create(name="Django", category="Programming")
        self.vacancy = Vacancy.objects.create(
            employer=self.employer_profile,
            title="Web Intern",
            description="desc",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.PUBLISHED,
        )
        VacancySkill.objects.create(vacancy=self.vacancy, skill=self.skill, required_level=3, weight=2, is_critical=False)
        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.skill, level=3)

    def test_student_can_access_recommendation_page(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("matching:student_recommendations"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Рекомендуемые вакансии")
        self.assertContains(response, "Web Intern")

    def test_employer_cannot_access_student_recommendations(self):
        self.client.force_login(self.employer_user)
        response = self.client.get(reverse("matching:student_recommendations"))
        self.assertEqual(response.status_code, 403)


class SkillWheelTests(TestCase):
    def setUp(self):
        self.student_user = get_user_model().objects.create_user(
            email="wheel.student@example.com",
            password="StrongPass123!",
            role="student",
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            full_name="Wheel Student",
            university="KRSU",
            faculty="CS",
            course=2,
            bio="",
            contact_info="",
        )

        self.python = Skill.objects.create(name="Python", category=Skill.Category.BACKEND)
        self.react = Skill.objects.create(name="React", category=Skill.Category.FRONTEND)
        self.git = Skill.objects.create(name="Git", category=Skill.Category.CORE_SKILLS)

    def test_compute_skill_wheel_returns_categories(self):
        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.python, level=4)
        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.react, level=4)
        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.git, level=5)

        categories = compute_skill_wheel(self.student_profile)

        self.assertEqual(len(categories), 6)
        frontend = next(item for item in categories if item["slug"] == "frontend")
        self.assertEqual(frontend["skills_total"], 5)
        self.assertIn("React", frontend["matched_skills"])
        self.assertEqual(frontend["score"], 33)
        self.assertEqual(frontend["student_total_skills"], 3)
        self.assertIn("market_score", frontend)

    def test_compute_skill_wheel_market_score_uses_direction_vacancy_share(self):
        employer_user = get_user_model().objects.create_user(
            email="wheel-employer@example.com",
            password="StrongPass123!",
            role="employer",
        )
        employer_profile = EmployerProfile.objects.create(
            user=employer_user,
            company_name="Market Corp",
            company_description="desc",
            contact_email="hr@market.example",
            website="",
        )
        frontend_vacancy = Vacancy.objects.create(
            employer=employer_profile,
            title="Frontend Intern",
            description="desc",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.PUBLISHED,
        )
        backend_vacancy = Vacancy.objects.create(
            employer=employer_profile,
            title="Backend Intern",
            description="desc",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.PUBLISHED,
        )
        VacancySkill.objects.create(
            vacancy=frontend_vacancy,
            skill=self.react,
            required_level=2,
            weight=1,
            is_critical=False,
        )
        VacancySkill.objects.create(
            vacancy=backend_vacancy,
            skill=self.python,
            required_level=2,
            weight=1,
            is_critical=False,
        )

        categories = compute_skill_wheel(self.student_profile)
        frontend = next(item for item in categories if item["slug"] == "frontend")
        self.assertEqual(frontend["market_score"], 50)
        self.assertEqual(frontend["market_vacancies_count"], 1)
        self.assertEqual(frontend["market_total_vacancies"], 2)
        self.assertIn("React", frontend["market_skills"])

    def test_skill_wheel_api_returns_json(self):
        self.client.force_login(self.student_user)
        response = self.client.get("/api/skill-wheel/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("categories", body)
        self.assertEqual(len(body["categories"]), 6)
        self.assertIn("market_score", body["categories"][0])

    def test_next_skill_recommendations_excludes_existing_student_skills(self):
        employer_user = get_user_model().objects.create_user(
            email="reco-employer@example.com",
            password="StrongPass123!",
            role="employer",
        )
        employer_profile = EmployerProfile.objects.create(
            user=employer_user,
            company_name="Reco Corp",
            company_description="desc",
            contact_email="hr@reco.example",
            website="",
        )
        vacancy = Vacancy.objects.create(
            employer=employer_profile,
            title="ML Intern",
            description="desc",
            requirements_text="",
            location="",
            internship_type=Vacancy.InternshipType.REMOTE,
            status=Vacancy.Status.PUBLISHED,
        )

        extra_skill = Skill.objects.create(name="Docker", category=Skill.Category.DEVOPS)
        StudentSkill.objects.create(student_profile=self.student_profile, skill=self.react, level=4)
        VacancySkill.objects.create(vacancy=vacancy, skill=self.react, required_level=3, weight=5, is_critical=True)
        VacancySkill.objects.create(vacancy=vacancy, skill=extra_skill, required_level=3, weight=6, is_critical=True)

        result = compute_next_skill_recommendations(self.student_profile, limit=3)

        names = [item["name"] for item in result]
        self.assertIn("Docker", names)
        self.assertNotIn("React", names)
