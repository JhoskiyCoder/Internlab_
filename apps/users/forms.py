from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class UserRegistrationForm(UserCreationForm):
    """Simple registration form with role choice for diploma project."""

    class Meta:
        model = get_user_model()
        fields = ("email", "role", "password1", "password2")
        labels = {
            "email": "Эл. почта",
            "role": "Роль",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                                                                 
        self.fields["role"].choices = [
            choice for choice in self.fields["role"].choices if choice[0] in {"student", "employer"}
        ]
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "student@example.com"})
        self.fields["role"].widget.attrs.update({"class": "form-select"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})


class UserLoginForm(AuthenticationForm):
    """Bootstrap-styled login form for Django LoginView."""

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Логин или эл. почта"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Пароль"}))
