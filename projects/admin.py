from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "status",
        "created_at",
        "participants_list",
    )
    list_editable = ("status",)
    list_filter = ("status", "created_at")
    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__name",
        "owner__surname",
    )
    ordering = ("-created_at",)
    filter_horizontal = ("participants",)

    @admin.display(description="Участники")
    def participants_list(self, obj):
        return ", ".join(str(user) for user in obj.participants.all())
