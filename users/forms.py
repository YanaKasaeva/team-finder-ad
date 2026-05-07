import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User


def normalize_phone(phone):
    phone = phone.strip()
    if re.fullmatch(r"8\d{10}", phone):
        return "+7" + phone[1:]
    if re.fullmatch(r"\+7\d{10}", phone):
        return phone
    raise forms.ValidationError(
        "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
    )


def validate_github_url(url):
    if not url:
        return url
    host = urlparse(url).netloc.lower()
    if host not in {"github.com", "www.github.com"}:
        raise forms.ValidationError("Ссылка должна вести именно на GitHub")
    return url


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
        # Телефон обязателен в модели, но отсутствует на форме регистрации по заданию.
        # Поэтому создаём технический уникальный номер, который пользователь потом поменяет в профиле.
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
