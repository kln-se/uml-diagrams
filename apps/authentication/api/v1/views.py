from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.api.v1.serializers import CustomAuthTokenSerializer
from apps.authentication.apps import AuthenticationConfig
from docs.api.templates.parameters import required_header_auth_parameter


# region @extend_schema
@extend_schema(
    tags=[AuthenticationConfig.tag],
    summary="Log in the user",
    description="This API endpoint allows user to log in and receive an \
    authentication token. This token should be placed in the *Authorization* header in \
    subsequent API calls. The token should be provided in the following format: \
    **Token <token-value>**",
    responses={
        200: CustomAuthTokenSerializer,
        400: OpenApiResponse(
            description="Errors:\n- Invalid credentials;\n- JSON parse error."
        ),
    },
)
# endregion
class CustomObtainAuthToken(ObtainAuthToken):
    """
    This API endpoint allows user to log in and receive an authentication token.
    """

    permission_classes = [AllowAny]
    serializer_class = CustomAuthTokenSerializer


# region @extend_schema
@extend_schema(
    tags=[AuthenticationConfig.tag],
    summary="Log out the user",
    description="This API endpoint allows user to log out the user. "
    "Drop authentication token.",
    parameters=[required_header_auth_parameter],
    responses={
        204: OpenApiResponse(description="Logged out successfully"),
        401: OpenApiResponse(description="Invalid token or token not provided"),
    },
)
# endregion
class LogoutAPIView(APIView):
    """
    This API endpoint allows user to log out. Drop the authentication token.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = None

    @staticmethod
    def post(request: Request) -> Response:
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
