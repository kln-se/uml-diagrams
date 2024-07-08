from django.urls import path

from apps.users.api.v1 import views

urlpatterns = [
    path("signup/", views.SignupUserAPIView.as_view(), name="signup"),
]
