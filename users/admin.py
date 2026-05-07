from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = (
        "email",
        "name",
        "surname",
        "phone",
        "is_active",
        "is_staff",
        "participated_projects_count",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "name", "surname", "phone")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions", "favorites")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личная информация",
            {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")},
        ),
        ("Избранное", {"fields": ("favorites",)}),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "phone",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(participated_count=Count("participated_projects", distinct=True))
        )

    @admin.display(description="Проектов участвует", ordering="participated_count")
    def participated_projects_count(self, obj):
        return obj.participated_count
