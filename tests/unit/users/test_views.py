from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.users.api.v1.serializers import SignupUserSerializer, UserSerializer
from apps.users.api.v1.views import SignupUserAPIView, UserViewSet


class TestUserViewSet:
    def test_get_serializer_class_returns_user_serializer(self):
        viewset = UserViewSet()
        assert viewset.get_serializer_class() == UserSerializer

    def test_user_viewset_permission_class_correct(self):
        viewset = UserViewSet()
        assert viewset.permission_classes == [IsAuthenticated]


class TestSignupUserAPIView:
    def test_get_serializer_class_returns_user_signup_serializer(self):
        viewset = SignupUserAPIView()
        assert viewset.get_serializer_class() == SignupUserSerializer

    def test_user_viewset_permission_class_correct(self):
        viewset = SignupUserAPIView()
        assert viewset.permission_classes == [AllowAny]
