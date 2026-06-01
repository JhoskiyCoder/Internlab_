"""Сервисы сопоставления для рекомендаций вакансий.

Логика рекомендаций вынесена в отдельный сервисный слой, чтобы она была:
1. прозрачной для защиты диплома,
2. удобной для тестирования,
3. отделенной от views и templates.
"""

from dataclasses import dataclass

from django.utils.text import slugify

from apps.skills.models import Skill, StudentSkill
from apps.vacancies.models import Vacancy, VacancySkill


@dataclass
class MatchingResult:
    vacancy: Vacancy
    score: float
    matched_skills_count: int
    missing_skills: list[str]
    missing_critical_skills: bool


SKILL_WHEEL_CATEGORY_SKILLS = {
    "Frontend": ["JavaScript", "TypeScript", "React", "HTML/CSS", "Next.js"],
    "Backend": ["Python", "Node.js", "Java", "PostgreSQL", "REST API"],
    "DevOps": ["Docker", "Kubernetes", "Linux", "CI/CD", "AWS"],
    "Data Science": ["Python", "Pandas", "NumPy", "SQL", "Scikit-learn"],
    "ML": ["PyTorch", "TensorFlow", "Scikit-learn", "Hugging Face", "OpenCV"],
    "Core Skills": ["Git", "HTTP", "Linux", "SQL", "Algorithms"],
}


def _normalize_skill_name(value: str) -> str:
    return value.strip().lower()


def _skill_category_to_wheel_category(category: str) -> str | None:
    """Сопоставить категорию навыка с осью карты навыков."""

    if category == Skill.Category.MACHINE_LEARNING:
        return "ML"
    if category in SKILL_WHEEL_CATEGORY_SKILLS:
        return category
    return None


def _get_market_requirements_by_vacancy() -> list[list[VacancySkill]]:
    """Вернуть требования опубликованных вакансий, сгруппированные по вакансии."""

    published_vacancies = Vacancy.objects.filter(status=Vacancy.Status.PUBLISHED).prefetch_related(
        "required_skills__skill"
    )
    return [list(vacancy.required_skills.all()) for vacancy in published_vacancies]


def _get_primary_market_categories(requirements_by_vacancy: list[list[VacancySkill]]) -> list[str | None]:
    """Определить основное направление каждой вакансии по сумме весов навыков.

    Вакансия может содержать общие навыки вроде Git, Python или SQL, поэтому
    простое наличие навыка раздувает сразу несколько направлений. Для карты
    рынка считаем основное направление вакансии: суммируем веса требований по
    категориям и выбираем категорию с наибольшим весом.
    """

    category_skill_names = {
        category_name: {_normalize_skill_name(skill_name) for skill_name in skills}
        for category_name, skills in SKILL_WHEEL_CATEGORY_SKILLS.items()
    }

    primary_categories = []
    for requirements in requirements_by_vacancy:
        category_weights = dict.fromkeys(SKILL_WHEEL_CATEGORY_SKILLS, 0)

        for requirement in requirements:
            skill_name = _normalize_skill_name(requirement.skill.name)
            for category_name, skill_names in category_skill_names.items():
                if skill_name in skill_names:
                    category_weights[category_name] += requirement.weight

        best_category = max(category_weights, key=category_weights.get)
        primary_categories.append(best_category if category_weights[best_category] else None)

    return primary_categories


def compute_skill_wheel(student_profile):
    """Посчитать распределение навыков и вакансий по категориям.

    Формула для студента:
        score = (student_skills_in_category / student_skills_total) * 100

    Формула для рынка:
        market_score = (primary_vacancies_in_category / published_vacancies_total) * 100

    Обе линии на графике теперь показывают одну и ту же сущность: долю
    направления. Поэтому `Вы` и `Рынок` можно визуально сравнивать между собой.

    Здесь `market_score` показывает долю опубликованных вакансий, у которых
    выбранное направление является основным. Основное направление определяется
    по сумме весов требований вакансии. Так Git, Python или SQL не превращают
    каждую вакансию сразу в Core/Backend/Data Science.

    - если у студента нет навыков, score = 0;
    - если опубликованных вакансий нет, market_score = 0;
    - результат возвращается как список словарей, готовых для JSON и шаблонов.
    """

    student_skill_items = StudentSkill.objects.filter(student_profile=student_profile).select_related("skill")
    student_skills_by_category = {category_name: [] for category_name in SKILL_WHEEL_CATEGORY_SKILLS}

    for item in student_skill_items:
        category_name = _skill_category_to_wheel_category(item.skill.category)
        if category_name:
            student_skills_by_category[category_name].append(item.skill.name)

    student_skills_total = sum(len(skill_names) for skill_names in student_skills_by_category.values())

    market_requirements_by_vacancy = _get_market_requirements_by_vacancy()
    primary_market_categories = _get_primary_market_categories(market_requirements_by_vacancy)
    market_skill_names = {
        _normalize_skill_name(requirement.skill.name)
        for requirements in market_requirements_by_vacancy
        for requirement in requirements
    }
    published_vacancies_total = len(market_requirements_by_vacancy)

    categories = []
    for category_name, skills in SKILL_WHEEL_CATEGORY_SKILLS.items():
        normalized_skills = {_normalize_skill_name(skill_name): skill_name for skill_name in skills}
        matched = student_skills_by_category[category_name]
        market_matched = [
            original_name
            for normalized_name, original_name in normalized_skills.items()
            if normalized_name in market_skill_names
        ]
        market_vacancies_count = primary_market_categories.count(category_name)
        skills_total = len(skills)
        skills_matched = len(matched)
        market_skills_matched = len(market_matched)
        score = round((skills_matched / student_skills_total) * 100) if student_skills_total else 0
        market_score = (
            round((market_vacancies_count / published_vacancies_total) * 100)
            if published_vacancies_total
            else 0
        )
        categories.append(
            {
                "name": category_name,
                "slug": slugify(category_name),
                "score": int(score),
                "market_score": int(market_score),
                "skills_total": skills_total,
                "skills_matched": skills_matched,
                "matched_skills": matched,
                "student_total_skills": student_skills_total,
                "market_skills_matched": market_skills_matched,
                "market_skills": market_matched,
                "market_vacancies_count": market_vacancies_count,
                "market_total_vacancies": published_vacancies_total,
            }
        )
    return categories


def compute_next_skill_recommendations(student_profile, limit: int = 3):
    """Вернуть навыки для прокачки на основе спроса опубликованных вакансий.

    Подход:
    - берем только опубликованные вакансии;
    - исключаем навыки, которые уже есть у студента;
    - считаем «сигнал спроса» навыка как сумму:
      `weight` + бонус за критичность + частота встречаемости;
    - сортируем по убыванию сигнала и отдаем top-N.
    """

    student_skill_ids = set(
        StudentSkill.objects.filter(student_profile=student_profile).values_list("skill_id", flat=True)
    )

    published_vacancies_count = Vacancy.objects.filter(status=Vacancy.Status.PUBLISHED).count()

    market_requirements = (
        VacancySkill.objects.filter(vacancy__status=Vacancy.Status.PUBLISHED)
        .exclude(skill_id__in=student_skill_ids)
        .select_related("skill")
    )

    aggregated = {}
    for requirement in market_requirements:
        entry = aggregated.setdefault(
            requirement.skill_id,
            {
                "name": requirement.skill.name,
                "market_signal": 0,
                "vacancies_count": 0,
                "critical_count": 0,
            },
        )
        entry["vacancies_count"] += 1
        entry["critical_count"] += int(requirement.is_critical)
        entry["market_signal"] += requirement.weight + (2 if requirement.is_critical else 0)

    recommendations = []
    for entry in aggregated.values():
        entry["market_signal"] += entry["vacancies_count"]
        entry["market_percent"] = (
            round((entry["vacancies_count"] / published_vacancies_count) * 100) if published_vacancies_count else 0
        )

        if entry["critical_count"] >= 2 or entry["market_percent"] >= 60:
            entry["priority"] = "important"
            entry["priority_label"] = "Важно"
            entry["hint"] = f"Нужен в {entry['market_percent']}% вакансий по вашему направлению"
        elif entry["market_percent"] >= 35:
            entry["priority"] = "recommended"
            entry["priority_label"] = "Желательно"
            entry["hint"] = f"Требуется в {entry['market_percent']}% вакансий"
        else:
            entry["priority"] = "plus"
            entry["priority_label"] = "Плюс"
            entry["hint"] = "Полезен для расширения профиля и роли"
        recommendations.append(entry)

    recommendations.sort(
        key=lambda item: (item["market_signal"], item["critical_count"], item["vacancies_count"], item["name"]),
        reverse=True,
    )
    return recommendations[:limit]


def calculate_vacancy_match(student_profile, vacancy: Vacancy) -> MatchingResult:
    """Рассчитать взвешенный процент совпадения студента и вакансии.

    Базовая формула:
        score = sum(skill_match * weight) / sum(weight) * 100
    where skill_match = min(student_level / required_level, 1)

    Пояснение:
    - `skill_match` находится в диапазоне [0, 1], где 1 означает, что студент
      полностью закрывает или превышает требуемый уровень навыка.
    - `weight` задает важность навыка в итоговой оценке:
      чем больше вес, тем сильнее его влияние на результат.
    - Если требуемого навыка нет, `student_level = 0`, вклад этого навыка
      в оценку равен 0, а навык попадает в `missing_skills`.
    - Если отсутствует хотя бы один критичный навык, применяется штраф
      `score * 0.8` (уменьшение на 20%).

    Итоговый балл округляется до 1 знака после запятой для удобного отображения.
    Логика остается простой и детерминированной для учебного проекта.
    """

    requirements = list(vacancy.required_skills.all())

    if not requirements:
        return MatchingResult(
            vacancy=vacancy,
            score=100.0,
            matched_skills_count=0,
            missing_skills=[],
            missing_critical_skills=False,
        )

    student_levels = {
        item.skill_id: item.level
        for item in StudentSkill.objects.filter(student_profile=student_profile).select_related("skill")
    }

                                         
                                              
                                
    weighted_sum = 0.0
    total_weight = 0
    matched_count = 0
    missing_skills: list[str] = []
    missing_critical = False

    for requirement in requirements:
        student_level = student_levels.get(requirement.skill_id, 0)
        skill_match = min(student_level / requirement.required_level, 1) if requirement.required_level else 0

        weighted_sum += skill_match * requirement.weight
        total_weight += requirement.weight

        if student_level > 0:
            matched_count += 1
        else:
            missing_skills.append(requirement.skill.name)
            if requirement.is_critical:
                missing_critical = True

                                                                   
    score = (weighted_sum / total_weight) * 100 if total_weight else 0.0
    if missing_critical:
                                                
        score *= 0.8

    return MatchingResult(
        vacancy=vacancy,
        score=round(score, 1),
        matched_skills_count=matched_count,
        missing_skills=missing_skills,
        missing_critical_skills=missing_critical,
    )


def get_recommended_vacancies(student_profile):
    """Вернуть опубликованные вакансии, отсортированные по совпадению.

    Правило ранжирования:
    - для каждой опубликованной вакансии отдельно считается совпадение
      через `calculate_vacancy_match`;
    - результаты сортируются по убыванию `score`.
    """

    vacancies = (
        Vacancy.objects.filter(status=Vacancy.Status.PUBLISHED)
        .select_related("employer")
        .prefetch_related("required_skills__skill")
    )
    results = [calculate_vacancy_match(student_profile, vacancy) for vacancy in vacancies]
    return sorted(results, key=lambda item: item.score, reverse=True)
