from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.users.api.v1.serializers import SignupUserSerializer
from apps.users.apps import UsersConfig


# region @extend_schema
@extend_schema(
    tags=[UsersConfig.tag],
    summary="Register a new user",
    description="This API endpoint allows to register a new user with \
    the provided email and password.",
    responses={
        201: SignupUserSerializer,
        400: OpenApiResponse(description="Bad request"),
    },
)
# endregion
class SignupUserAPIView(generics.CreateAPIView):
    """
    API endpoint that allows to register a new user.
    """

    serializer_class = SignupUserSerializer
    permission_classes = [AllowAny]
