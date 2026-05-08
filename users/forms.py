from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from team_finder.validators import validate_github_url
from users.models import User
from users.services import normalize_phone


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if not user.phone:
            user.phone = self._make_temp_phone()

        if commit:
            user.save()

        return user

    @staticmethod
    def _make_temp_phone():
        """Создает технический уникальный телефон для формы регистрации."""
        prefix = "+7999"
        number = User.objects.count() + 1
        phone = f"{prefix}{number:07d}"

        while User.objects.filter(phone=phone).exists():
            number += 1
            phone = f"{prefix}{number:07d}"

        return phone


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный имейл или пароль")

            cleaned_data["user"] = user

        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data["phone"])
        users = User.objects.filter(phone=phone)

        if self.instance.pk:
            users = users.exclude(pk=self.instance.pk)

        if users.exists():
            raise forms.ValidationError("Такой телефон уже используется")

        return phone

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url"))


class UserPasswordChangeForm(PasswordChangeForm):
    pass
