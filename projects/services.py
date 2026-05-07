from .models import Project


def get_projects_queryset():
    return (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )


def get_project_queryset():
    return Project.objects.select_related("owner").prefetch_related("participants")


def get_favorite_projects_queryset(user):
    return (
        user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
