from django.contrib import admin

from apps.diagrams.models import Diagram


class DiagramAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "created_at",
        "updated_at",
    )
    search_fields = ["title", "owner__email"]


admin.site.register(Diagram, DiagramAdmin)
