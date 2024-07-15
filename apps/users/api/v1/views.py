from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.users.api.v1.serializers import SignupUserSerializer, UserSerializer
from apps.users.apps import UsersConfig
from docs.api.templates.parameters import required_header_auth_parameter


# region @extend_schema
@extend_schema(
    tags=[UsersConfig.tag],
    summary="Register a new user",
    description="This API endpoint allows to register a new user with \
    the provided email and password.",
    responses={
        201: SignupUserSerializer,
        400: OpenApiResponse(
            description="Errors:"
            "\n- Email or password validation errors;"
            "\n- User already exists (same email);"
            "\n- JSON parse error."
        ),
    },
)
# endregion
class SignupUserAPIView(generics.CreateAPIView):
    """
    API endpoint that allows to register a new user.
    """

    serializer_class = SignupUserSerializer
    permission_classes = [AllowAny]


# region @extend_schema
@extend_schema_view(
    retrieve=extend_schema(
        tags=[UsersConfig.tag],
        summary="Retrieve a current logged in user",
        description="Returns the details of a logged in user based on \
        the authentication token.",
        parameters=[required_header_auth_parameter],
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Invalid token or token not provided"),
        },
    ),
    update=extend_schema(
        tags=[UsersConfig.tag],
        summary="Update a current logged in user info",
        description="Updates the details of a logged in user based on \
        the authentication token.",
        parameters=[required_header_auth_parameter],
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Email or password validation error"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
        },
    ),
    partial_update=extend_schema(
        tags=[UsersConfig.tag],
        summary="Partially update a current logged in user info",
        description="Partially updates the details of a logged in user based on \
        the authentication token.",
        parameters=[required_header_auth_parameter],
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Email or password validation error"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
        },
    ),
)
# endregion
class UserViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """
    API endpoint that allows to retrieve or update the current user.
    """

    http_method_names = ["get", "head", "put", "patch"]
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
