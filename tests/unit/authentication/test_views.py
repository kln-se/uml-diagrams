from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.authentication.api.v1.serializers import CustomAuthTokenSerializer
from apps.authentication.api.v1.views import CustomObtainAuthToken, LogoutAPIView


class TestCustomObtainAuthToken:
    def test_custom_obtain_auth_token_token_contains_correct_serializer(self):
        viewset = CustomObtainAuthToken()
        assert viewset.serializer_class == CustomAuthTokenSerializer

    def test_user_viewset_permission_class_correct(self):
        viewset = CustomObtainAuthToken()
        assert viewset.permission_classes == [AllowAny]


class TestLogoutAPIView:
    def test_logout_api_view_permission_class_correct(self):
        viewset = LogoutAPIView()
        assert viewset.permission_classes == [IsAuthenticated]
