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
    search_fields = ("diagram__title", "shared_to__email")


admin.site.register(Collaborator, CollaboratorAdmin)
