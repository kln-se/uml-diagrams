from django.contrib import admin

from apps.users.models import User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
        "last_login",
    )


admin.site.register(User, CustomUserAdmin)
