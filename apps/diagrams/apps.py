from django.apps import AppConfig


class DiagramsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.diagrams"
    tag = name.split(".")[-1]
