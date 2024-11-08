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


def save_diagram(self: GenericViewSet, request: Request, **_kwargs) -> Response:
    """
    API endpoint that allows to save changes to an existing shared diagram.
    If the diagram was shared to a user with appropriate "view-edit" permission,
    it can be edited, and the changes will be saved.
    """
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    if getattr(instance, "_prefetched_objects_cache", None):
        # If 'prefetch_related' has been applied to a queryset, we need to
        # forcibly invalidate the prefetch cache on the instance.
        instance._prefetched_objects_cache = {}

    return Response(serializer.data, status=status.HTTP_200_OK)
