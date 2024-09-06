from typing import Union

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


def invite_collaborator(
    self: Union[ModelViewSet, CreateAPIView], request: Request, **_
) -> Response:
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
