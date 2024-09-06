from django.contrib import admin

from apps.sharings.models import Collaborator


class CollaboratorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "diagram",
        "shared_to",
        "permission_level",
        "shared_at",
    )

    fields = ("diagram", "shared_to", "permission_level")


admin.site.register(Collaborator, CollaboratorAdmin)
