from django import forms
from .models import Application


class ApplicationCreateForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ("cover_letter",)
        labels = {"cover_letter": "Сопроводительное письмо"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cover_letter"].widget.attrs.update(
            {
                "class": "form-control",
                "rows": 6,
                "placeholder": "Кратко опишите ваш опыт и мотивацию.",
            }
        )


class ApplicationStatusForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ("status",)
        labels = {"status": "Статус заявки"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].widget.attrs["class"] = "form-select"
        self.fields["status"].choices = Application.Status.choices
