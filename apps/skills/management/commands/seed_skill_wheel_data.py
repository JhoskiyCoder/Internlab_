from django.core.management.base import BaseCommand

from apps.matching.services import SKILL_WHEEL_CATEGORY_SKILLS
from apps.skills.models import Skill


CATEGORY_TO_CHOICE = {
    "Frontend": Skill.Category.FRONTEND,
    "Backend": Skill.Category.BACKEND,
    "DevOps": Skill.Category.DEVOPS,
    "Data Science": Skill.Category.DATA_SCIENCE,
    "ML": Skill.Category.MACHINE_LEARNING,
    "Core Skills": Skill.Category.CORE_SKILLS,
}


class Command(BaseCommand):
    help = "Seed default skill-wheel categories/skills for MVP demo"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        first_category_for_skill = {}
        for category_name, skill_names in SKILL_WHEEL_CATEGORY_SKILLS.items():
            for skill_name in skill_names:
                first_category_for_skill.setdefault(skill_name, category_name)

        for skill_name, category_name in first_category_for_skill.items():
            category_value = CATEGORY_TO_CHOICE.get(category_name, Skill.Category.CORE_SKILLS)
            obj, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={"category": category_value},
            )
            if created:
                created_count += 1
            elif obj.category != category_value:
                obj.category = category_value
                obj.save(update_fields=["category"])
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Skill wheel seed completed. Created: {created_count}, Updated: {updated_count}"
            )
        )
