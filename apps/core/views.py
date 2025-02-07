from django.http import HttpRequest, JsonResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


def health_check(_request: HttpRequest) -> JsonResponse:
    """Health check endpoint."""
    return JsonResponse(data={"status": "ok"}, status=HTTP_200_OK)


class CustomHttpErrorViews:
    """
    This class ensures that Django returns JSON responses instead of
    HTML error pages for unhandled exceptions. In some cases, errors
    that are not managed by Django REST Framework (DRF) are processed
    by Django's default error handling, resulting in HTML responses.

    To maintain consistency in API responses, this class defines
    custom views that override Django's default HTTP error views.
    """

    @staticmethod
    def bad_request_view(request, exception):
        return JsonResponse({"detail": "Bad request"}, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    def permission_denied_view(request, exception):
        return JsonResponse({"detail": "Permission denied"}, status=HTTP_403_FORBIDDEN)

    @staticmethod
    def page_not_found_view(request, exception):
        return JsonResponse({"detail": "Not found"}, status=HTTP_404_NOT_FOUND)

    @staticmethod
    def server_error_view(request):
        return JsonResponse(
            {"detail": "Server error"}, status=HTTP_500_INTERNAL_SERVER_ERROR
        )
