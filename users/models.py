import random
from io import BytesIO

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("name", "Admin")
        extra_fields.setdefault("surname", "Admin")
        extra_fields.setdefault("phone", "+70000000000")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser должен иметь is_superuser=True")

        return self.create_user(email, password, **extra_fields)


def generate_avatar(name):
    letter = (name[:1] or "U").upper()
    colors = [
        (93, 156, 236),
        (72, 207, 173),
        (255, 206, 84),
        (172, 146, 236),
        (150, 180, 210),
    ]
    image = Image.new("RGB", (200, 200), random.choice(colors))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 110)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    draw.text(
        ((200 - width) / 2, (200 - height) / 2 - 8),
        letter,
        fill=(255, 255, 255),
        font=font,
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{letter}.png")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True)
    phone = models.CharField("Телефон", max_length=12, unique=True)
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    about = models.TextField("О себе", max_length=256, blank=True)
    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
        verbose_name="Избранные проекты",
    )

    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Администратор", default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    class Meta:
        ordering = ["-id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.save(
                f"avatar_{self.name or 'user'}.png",
                generate_avatar(self.name),
                save=False,
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.surname}"
