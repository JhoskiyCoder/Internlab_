from django import forms
from apps.skills.forms import StudentSkillForm
from apps.skills.models import Skill
from .models import Vacancy, VacancySkill


class SkillChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.category})"


class VacancyForm(forms.ModelForm):

    class Meta:
        model = Vacancy
        fields = (
            "title",
            "description",
            "requirements_text",
            "location",
            "internship_type",
            "status",
        )
        labels = {
            "title": "Название вакансии",
            "description": "Описание стажировки",
            "requirements_text": "Требования",
            "location": "Локация",
            "internship_type": "Формат работы",
            "status": "Статус вакансии",
        }
        help_texts = {
            "title": "Пример: Стажер Python Backend, Стажер Frontend React, Стажер DevOps.",
            "description": "Опишите задачи, инструменты и ожидаемые обязанности на стажировке.",
            "requirements_text": "Перечислите требуемые навыки и минимальные уровни владения.",
            "location": "Укажите город или формат локации, например: Бишкек, Алматы, Москва.",
            "status": "Черновик не виден студентам. Опубликованная вакансия появится в списке стажировок.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_skill_configs = []
        self._ensure_catalog_skills()
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            if name in {"internship_type", "status"}:
                field.widget.attrs["class"] = "form-select"
            if name in {"description", "requirements_text"}:
                field.widget.attrs["rows"] = 4
        self.fields["title"].widget.attrs[
            "placeholder"
        ] = "Например: Стажер Django Backend"
        self.fields["description"].widget.attrs[
            "placeholder"
        ] = "Опишите задачи стажировки и используемый стек."
        self.fields["requirements_text"].widget.attrs[
            "placeholder"
        ] = "Например: опыт с Python, Django, SQL и Git."
        self.fields["location"].widget.attrs["placeholder"] = "Например: Бишкек"
        self.fields["status"].widget = forms.HiddenInput()
        self.fields["selected_skills"] = forms.ModelMultipleChoiceField(
            queryset=Skill.objects.order_by("category", "name"),
            required=False,
            label="Ключевые навыки",
        )
        self.status_options = [
            {
                "value": Vacancy.Status.DRAFT,
                "label": "Черновик",
                "description": "Не видна студентам",
            },
            {
                "value": Vacancy.Status.PUBLISHED,
                "label": "Опубликована",
                "description": "Видна студентам",
            },
            {
                "value": Vacancy.Status.CLOSED,
                "label": "Закрыта",
                "description": "Без откликов",
            },
            {
                "value": Vacancy.Status.ARCHIVED,
                "label": "В архиве",
                "description": "Скрыта",
            },
        ]
        self.skill_catalog = self._build_skill_catalog()

    def _ensure_catalog_skills(self):
        seen_names = set()
        for _, _, category, technologies in StudentSkillForm.SKILL_CATALOG:
            for technology_name in technologies:
                if technology_name in seen_names:
                    continue
                seen_names.add(technology_name)
                Skill.objects.get_or_create(
                    name=technology_name, defaults={"category": category}
                )

    def _build_skill_catalog(self):
        selected_ids = set()
        if self.is_bound:
            selected_ids = set(self.data.getlist(self.add_prefix("selected_skills")))
        skills = Skill.objects.order_by("category", "name")
        name_to_skill_id = {item.name: item.pk for item in skills}
        catalog = []
        for key, label, _category, technologies in StudentSkillForm.SKILL_CATALOG:
            catalog.append(
                {
                    "key": key,
                    "label": label,
                    "technologies": [
                        {
                            "name": technology_name,
                            "id": name_to_skill_id.get(technology_name),
                            "selected": str(name_to_skill_id.get(technology_name))
                            in selected_ids,
                            "level": (
                                self.data.get(
                                    f"skill_level_{name_to_skill_id.get(technology_name)}",
                                    "3",
                                )
                                if self.is_bound
                                and name_to_skill_id.get(technology_name)
                                else "3"
                            ),
                            "is_critical": (
                                self.data.get(
                                    f"skill_critical_{name_to_skill_id.get(technology_name)}"
                                )
                                == "on"
                                if self.is_bound
                                and name_to_skill_id.get(technology_name)
                                else False
                            ),
                            "icon_url": (
                                f"https://cdn.simpleicons.org/{StudentSkillForm.TECHNOLOGY_ICON_CONFIG[technology_name]['slug']}/{StudentSkillForm.TECHNOLOGY_ICON_CONFIG[technology_name]['color']}"
                                if StudentSkillForm.TECHNOLOGY_ICON_CONFIG.get(
                                    technology_name, {}
                                ).get("slug")
                                else None
                            ),
                            "short": StudentSkillForm.TECHNOLOGY_ICON_CONFIG.get(
                                technology_name, {}
                            ).get("short", technology_name[:2]),
                        }
                        for technology_name in technologies
                    ],
                }
            )
        return catalog

    def clean(self):
        cleaned_data = super().clean()
        selected_skills = cleaned_data.get("selected_skills") or []
        selected_skill_configs = []
        for skill in selected_skills:
            raw_level = self.data.get(f"skill_level_{skill.pk}", "3")
            try:
                required_level = int(raw_level)
            except (TypeError, ValueError):
                required_level = 3
            if required_level < 1 or required_level > 5:
                self.add_error(
                    "selected_skills", f"Некорректный уровень навыка: {skill.name}."
                )
                continue
            selected_skill_configs.append(
                {
                    "skill": skill,
                    "required_level": required_level,
                    "is_critical": self.data.get(f"skill_critical_{skill.pk}") == "on",
                }
            )
        self.selected_skill_configs = selected_skill_configs
        return cleaned_data


class VacancySkillForm(forms.ModelForm):

    class Meta:
        model = VacancySkill
        fields = ("skill", "required_level", "weight", "is_critical")
        labels = {
            "skill": "Навык",
            "required_level": "Требуемый уровень (1-5)",
            "weight": "Вес навыка",
            "is_critical": "Критичный навык",
        }

    def __init__(self, *args, **kwargs):
        self.vacancy = kwargs.pop("vacancy")
        super().__init__(*args, **kwargs)
        self._ensure_catalog_skills()
        queryset = Skill.objects.order_by("category", "name")
        self.fields["skill"] = SkillChoiceField(
            queryset=queryset, widget=forms.HiddenInput(), label="Навык"
        )
        self.fields["required_level"].widget = forms.HiddenInput()
        self.fields["weight"].widget = forms.HiddenInput()
        self.fields["required_level"].initial = self.instance.required_level or 1
        self.fields["weight"].initial = self.instance.weight or 1
        self.fields["is_critical"].widget.attrs["class"] = "form-check-input"
        name_to_skill_id = {item.name: item.pk for item in queryset}
        self.skill_catalog = []
        for key, label, _category, technologies in StudentSkillForm.SKILL_CATALOG:
            self.skill_catalog.append(
                {
                    "key": key,
                    "label": label,
                    "technologies": [
                        {
                            "name": technology_name,
                            "id": name_to_skill_id.get(technology_name),
                            "icon_url": (
                                f"https://cdn.simpleicons.org/{StudentSkillForm.TECHNOLOGY_ICON_CONFIG[technology_name]['slug']}/{StudentSkillForm.TECHNOLOGY_ICON_CONFIG[technology_name]['color']}"
                                if StudentSkillForm.TECHNOLOGY_ICON_CONFIG.get(
                                    technology_name, {}
                                ).get("slug")
                                else None
                            ),
                            "short": StudentSkillForm.TECHNOLOGY_ICON_CONFIG.get(
                                technology_name, {}
                            ).get("short", technology_name[:2]),
                        }
                        for technology_name in technologies
                    ],
                }
            )

    def _ensure_catalog_skills(self):
        seen_names = set()
        for _, _, category, technologies in StudentSkillForm.SKILL_CATALOG:
            for technology_name in technologies:
                if technology_name in seen_names:
                    continue
                seen_names.add(technology_name)
                Skill.objects.get_or_create(
                    name=technology_name, defaults={"category": category}
                )

    def clean_skill(self):
        skill = self.cleaned_data["skill"]
        queryset = VacancySkill.objects.filter(vacancy=self.vacancy, skill=skill)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError(
                "Этот навык уже добавлен в требования вакансии."
            )
        return skill

    def clean_weight(self):
        return 1
