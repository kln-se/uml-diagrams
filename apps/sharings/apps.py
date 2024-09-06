from django.apps import AppConfig


class SharingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sharings"
    tag = name.split(".")[-1]
