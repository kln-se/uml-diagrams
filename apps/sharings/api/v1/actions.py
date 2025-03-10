from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.sharings.constants import PermissionLevels
from apps.sharings.models import Collaborator


def invite_collaborator(self: ModelViewSet, request: Request, **_kwargs) -> Response:
    """
    API endpoint that allows to share an existing diagram with other users:
    create a new diagram share invitation.
    """
    diagram = self.get_object()
    context = self.get_serializer_context()
    context["diagram"] = diagram
    serializer = self.get_serializer(data=request.data, context=context)
    serializer.is_valid(raise_exception=True)
    serializer.save(diagram=diagram)
    headers = self.get_success_headers(serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def remove_all_collaborators(self: ModelViewSet, *_args, **_kwargs) -> Response:
    """
    API endpoint that allows to remove all existing collaborators from a
    certain diagram.
    """
    diagram = self.get_object()
    Collaborator.objects.filter(diagram=diagram).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def set_diagram_public(self: ModelViewSet, *_args, **_kwargs) -> Response:
    """
    API endpoint that allows to make a certain diagram public.
    """
    diagram = self.get_object()
    context = self.get_serializer_context()
    context["diagram"] = diagram
    serializer = self.get_serializer(context=context, data={}, allow_null=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(
        diagram=diagram, shared_to=None, permission_level=PermissionLevels.VIEWONLY
    )
    return Response(status=status.HTTP_201_CREATED)


def set_diagram_private(self: ModelViewSet, *_args, **_kwargs) -> Response:
    """
    API endpoint that allows to make a publicly shared diagram private.
    """
    diagram = self.get_object()
    Collaborator.objects.filter(diagram=diagram, shared_to=None).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
