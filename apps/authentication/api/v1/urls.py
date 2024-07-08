from django.urls import path

from apps.authentication.api.v1.views import CustomObtainAuthToken, LogoutAPIView

urlpatterns = [
    path("login/", CustomObtainAuthToken.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
