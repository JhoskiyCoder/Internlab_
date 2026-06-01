from django import forms
from django.contrib.auth import get_user_model

from .models import EmployerProfile, StudentProfile, StudentProject


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("full_name", "avatar", "university", "course", "bio")
        labels = {
            "full_name": "ФИО",
            "avatar": "Аватар",
            "university": "Университет",
            "course": "Курс",
            "bio": "О себе",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            if name == "bio":
                field.widget.attrs["rows"] = 4
        self.fields["avatar"].widget = forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": "image/*"}
        )
        self.fields["full_name"].widget.attrs["placeholder"] = "Например: Алексей Смирнов"
        self.fields["university"].widget.attrs["placeholder"] = "Например: НИУ ВШЭ"
        self.fields["course"].widget.attrs.update({"placeholder": "Например: 3", "min": 1, "max": 6})
        self.fields["bio"].widget.attrs["placeholder"] = "Коротко расскажите о себе, направлении и целях стажировки."


class StudentProfileSettingsForm(forms.ModelForm):
    email = forms.EmailField(label="Эл. почта")

    class Meta:
        model = StudentProfile
        fields = ("full_name", "avatar", "bio", "university", "course")
        labels = {
            "full_name": "ФИО",
            "avatar": "Аватар",
            "bio": "О себе",
            "university": "Университет",
            "course": "Курс",
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            if name == "bio":
                field.widget.attrs["rows"] = 4
        self.fields["avatar"].widget = forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": "image/*"}
        )

        if self.user:
            self.fields["email"].initial = self.user.email
        self.fields["email"].widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        queryset = get_user_model().objects.filter(email=email)
        if self.user:
            queryset = queryset.exclude(pk=self.user.pk)
        if queryset.exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
        if self.user:
            self.user.email = self.cleaned_data["email"]
            if commit:
                self.user.save(update_fields=["email"])
        return profile


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ("company_name", "logo", "company_description", "contact_email", "website")
        labels = {
            "company_name": "Название компании",
            "logo": "Логотип компании",
            "company_description": "Описание компании",
            "contact_email": "Контактный email",
            "website": "Сайт",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            if name == "company_description":
                field.widget.attrs["rows"] = 4
        self.fields["logo"].widget = forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": "image/*"}
        )


class StudentProjectForm(forms.ModelForm):
    class Meta:
        model = StudentProject
        fields = ("title", "role", "description", "start_date", "end_date", "is_current")
        labels = {
            "title": "Название проекта",
            "role": "Роль",
            "description": "Описание",
            "start_date": "Дата начала",
            "end_date": "Дата окончания",
            "is_current": "Проект в процессе",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            if name == "description":
                field.widget.attrs["rows"] = 3
        self.fields["start_date"].widget = forms.DateInput(attrs={"class": "form-control", "type": "date"})
        self.fields["end_date"].widget = forms.DateInput(attrs={"class": "form-control", "type": "date"})
        self.fields["is_current"].widget = forms.CheckboxInput(attrs={"class": "form-check-input"})
        self.fields["title"].widget.attrs["placeholder"] = "Например: Платформа онлайн-курсов"
        self.fields["role"].widget.attrs["placeholder"] = "Frontend-разработчик"
        self.fields["description"].widget.attrs["placeholder"] = "Кратко опишите ваш вклад и результат проекта"
