from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest

from apps.users.models import User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
        "last_login",
    )
    readonly_fields = ["date_joined", "last_login"]
    search_fields = ["email", "first_name", "last_name"]

    def save_model(self, request: WSGIRequest, obj: User, form, change: bool):
        """
        Override default save_model() method to hash password in case:
            - creating new user;
            - changing existing user's password.
        """
        new_password = form.cleaned_data["password"]
        if change:
            old_password = User.objects.get(id=obj.id).password
            if new_password != old_password:
                obj.set_password(new_password)
        else:
            obj.set_password(new_password)
        super().save_model(request, obj, form, change)


admin.site.register(User, CustomUserAdmin)
