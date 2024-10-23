from django.urls import path

from apps.core import views

urlpatterns = [
    path("", views.health_check, name="health-check"),
]
