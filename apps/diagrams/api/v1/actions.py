from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


def copy_diagram(self: GenericViewSet, request: Request, **_kwargs) -> Response:
    """
    API endpoint that allows to create a copy of an existing diagram.
    """
    original_diagram = self.get_object()
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.instance = original_diagram
    serializer.save(
        id=None,
        title=f"Copy of {original_diagram.title}",
        owner=self.request.user,
    )
    headers = CreateModelMixin().get_success_headers(serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
