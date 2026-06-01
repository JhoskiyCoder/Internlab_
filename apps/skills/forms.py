from django import forms
from .models import Skill, StudentSkill


class SkillChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.category})"


class StudentSkillForm(forms.ModelForm):
    TECHNOLOGY_ICON_CONFIG = {
        "JavaScript": {"slug": "javascript", "color": "F7DF1E", "short": "JS"},
        "TypeScript": {"slug": "typescript", "color": "3178C6", "short": "TS"},
        "React": {"slug": "react", "color": "61DAFB", "short": "R"},
        "HTML/CSS": {"slug": "html5", "color": "E34F26", "short": "H/C"},
        "Next.js": {"slug": "nextdotjs", "color": "000000", "short": "N"},
        "Python": {"slug": "python", "color": "3776AB", "short": "Py"},
        "Node.js": {"slug": "nodedotjs", "color": "339933", "short": "N"},
        "Java": {"slug": "openjdk", "color": "ED8B00", "short": "J"},
        "PostgreSQL": {"slug": "postgresql", "color": "4169E1", "short": "PG"},
        "REST API": {"slug": None, "color": None, "short": "API"},
        "Docker": {"slug": "docker", "color": "2496ED", "short": "D"},
        "Kubernetes": {"slug": "kubernetes", "color": "326CE5", "short": "K8s"},
        "Linux": {"slug": "linux", "color": "FCC624", "short": "L"},
        "CI/CD": {"slug": "githubactions", "color": "2088FF", "short": "CI"},
        "AWS": {"slug": "amazonwebservices", "color": "FF9900", "short": "AWS"},
        "Pandas": {"slug": "pandas", "color": "150458", "short": "Pd"},
        "NumPy": {"slug": "numpy", "color": "013243", "short": "Np"},
        "SQL": {"slug": None, "color": None, "short": "SQL"},
        "Scikit-learn": {"slug": "scikitlearn", "color": "F7931E", "short": "SK"},
        "PyTorch": {"slug": "pytorch", "color": "EE4C2C", "short": "PT"},
        "TensorFlow": {"slug": "tensorflow", "color": "FF6F00", "short": "TF"},
        "Hugging Face": {"slug": "huggingface", "color": "FFD21E", "short": "HF"},
        "OpenCV": {"slug": "opencv", "color": "5C3EE8", "short": "CV"},
        "Git": {"slug": "git", "color": "F05032", "short": "Git"},
        "HTTP": {"slug": None, "color": None, "short": "HTTP"},
        "Algorithms": {"slug": None, "color": None, "short": "Algo"},
    }
    SKILL_CATALOG = [
        (
            "frontend",
            "Frontend",
            Skill.Category.FRONTEND,
            ["JavaScript", "TypeScript", "React", "HTML/CSS", "Next.js"],
        ),
        (
            "backend",
            "Backend",
            Skill.Category.BACKEND,
            ["Python", "Node.js", "Java", "PostgreSQL", "REST API"],
        ),
        (
            "devops",
            "DevOps",
            Skill.Category.DEVOPS,
            ["Docker", "Kubernetes", "Linux", "CI/CD", "AWS"],
        ),
        (
            "data_science",
            "Data Science",
            Skill.Category.DATA_SCIENCE,
            ["Python", "Pandas", "NumPy", "SQL", "Scikit-learn"],
        ),
        (
            "machine_learning",
            "ML",
            Skill.Category.MACHINE_LEARNING,
            ["PyTorch", "TensorFlow", "Scikit-learn", "Hugging Face", "OpenCV"],
        ),
        (
            "core_skills",
            "Core Skills",
            Skill.Category.CORE_SKILLS,
            ["Git", "HTTP", "Linux", "SQL", "Algorithms"],
        ),
    ]

    class Meta:
        model = StudentSkill
        fields = ("skill", "level")

    def _ensure_catalog_skills(self):
        seen_names = set()
        for _, _, category, technologies in self.SKILL_CATALOG:
            for technology_name in technologies:
                if technology_name in seen_names:
                    continue
                seen_names.add(technology_name)
                Skill.objects.get_or_create(
                    name=technology_name, defaults={"category": category}
                )

    def __init__(self, *args, **kwargs):
        self.student_profile = kwargs.pop("student_profile")
        super().__init__(*args, **kwargs)
        self._ensure_catalog_skills()
        queryset = Skill.objects.order_by("name")
        self.fields["skill"] = SkillChoiceField(
            queryset=queryset, widget=forms.HiddenInput(), label="Навык"
        )
        self.fields["level"].widget = forms.HiddenInput()
        name_to_skill_id = {item.name: item.pk for item in queryset}
        self.skill_catalog = []
        for key, label, _category, technologies in self.SKILL_CATALOG:
            self.skill_catalog.append(
                {
                    "key": key,
                    "label": label,
                    "technologies": [
                        {
                            "name": technology_name,
                            "id": name_to_skill_id.get(technology_name),
                            "icon_url": (
                                f"https://cdn.simpleicons.org/{self.TECHNOLOGY_ICON_CONFIG[technology_name]['slug']}/{self.TECHNOLOGY_ICON_CONFIG[technology_name]['color']}"
                                if self.TECHNOLOGY_ICON_CONFIG.get(
                                    technology_name, {}
                                ).get("slug")
                                else None
                            ),
                            "short": self.TECHNOLOGY_ICON_CONFIG.get(
                                technology_name, {}
                            ).get("short", technology_name[:2]),
                        }
                        for technology_name in technologies
                    ],
                }
            )

    def clean_skill(self):
        skill = self.cleaned_data["skill"]
        queryset = StudentSkill.objects.filter(
            student_profile=self.student_profile, skill=skill
        )
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Этот навык уже добавлен в ваш профиль.")
        return skill
