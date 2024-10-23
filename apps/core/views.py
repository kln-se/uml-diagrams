from django.http import HttpRequest, JsonResponse
from rest_framework.status import HTTP_200_OK


def health_check(_request: HttpRequest) -> JsonResponse:
    """Health check endpoint."""
    return JsonResponse(data={"status": "ok"}, status=HTTP_200_OK)
