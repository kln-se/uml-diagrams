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

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(LogEntry, LogEntryAdmin)
