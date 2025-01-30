from django.contrib import admin
from django.contrib.admin.models import LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "action_time",
        "user",
        "content_type",
        "object_id",
        "action_flag",
        "change_message",
    )
    readonly_fields = list_display + ("object_repr",)
    list_filter = ("action_flag", "user", "content_type")
    ordering = ("-action_time",)


admin.site.register(LogEntry, LogEntryAdmin)
