from projects.models import Project


def get_projects_queryset(queryset=Project.objects):
    return (
        queryset.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
