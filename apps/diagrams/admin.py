from django.contrib import admin

from apps.diagrams.models import Diagram


class DiagramAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "owner",
        "created_at",
        "updated_at",
    )


admin.site.register(Diagram, DiagramAdmin)
