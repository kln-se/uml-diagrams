from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.apps import AuthenticationConfig


# region @extend_schema
@extend_schema(
    tags=[AuthenticationConfig.tag],
    summary="Log in the user",
    description="This API endpoint allows user to log in and receive an \
    authentication token. This token should be placed in the *Authorization* header in \
    subsequent API calls. The token should be provided in the following format: \
    **Token <token-value>**",
    responses={
        200: OpenApiResponse(description="Logged in successfully"),
        400: OpenApiResponse(description="Invalid credentials"),
    },
)
# endregion
class CustomObtainAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]


# region @extend_schema
@extend_schema(
    tags=[AuthenticationConfig.tag],
    summary="Log out the user",
    description="This API endpoint allows user to log out the user. "
    "Drop authentication token.",
    parameters=[
        OpenApiParameter(
            name="Authorization",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            description="Authentication token in the following format: "
            "**Token <token-value>**",
            default="Token <token-value>",
        )
    ],
    responses={
        204: OpenApiResponse(description="Logged out successfully"),
        401: OpenApiResponse(description="Invalid token"),
    },
)
# endregion
class LogoutAPIView(APIView):
    """Log out the user. Drop authentication token."""

    permission_classes = [IsAuthenticated]
    serializer_class = None

    @staticmethod
    def post(request: Request) -> Response:
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
