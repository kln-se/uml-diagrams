from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.authentication.api.v1.permissions import IsAdminOrIsOwner
from apps.diagrams.api.v1.serializers import DiagramCopySerializer, DiagramSerializer
from apps.diagrams.apps import DiagramsConfig
from apps.diagrams.models import Diagram


# region @extend_schema
@extend_schema_view(
    list=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="List diagrams",
        description="Returns a list of all available diagrams.",
    ),
    create=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Create a new diagram",
        description="Creates a new diagram based on the provided data.",
        request=DiagramSerializer,
        responses={201: DiagramSerializer},
    ),
    retrieve=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Retrieve a diagram",
        description="Returns the details of a specific diagram.",
        responses={200: DiagramSerializer},
    ),
    update=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Update a diagram",
        description="Updates the details of a specific diagram.",
        request=DiagramSerializer,
        responses={200: DiagramSerializer},
    ),
    partial_update=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Partially update a diagram",
        description="Partially updates the details of a specific diagram.",
        request=DiagramSerializer,
        responses={200: DiagramSerializer},
    ),
    destroy=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Delete a diagram",
        description="Deletes a specific diagram.",
        responses={204: None},
    ),
)
# endregion
class DiagramViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows:
    - view all diagrams;
    - store a new diagram;
    - view, edit or delete an existing diagram.
    """

    queryset: QuerySet[Diagram] = Diagram.objects.all()
    serializer_class = DiagramSerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsOwner]

    def get_queryset(self) -> QuerySet[Diagram]:
        """
        Filter the queryset based on the user's permissions:
        - if the user is an admin, return all diagrams;
        - otherwise, return only the diagrams that belong to the user.
        """
        if self.request.user.is_admin:
            return self.queryset
        return self.queryset.filter(owner=self.request.user)

    def perform_update(self, serializer: DiagramSerializer) -> None:
        """
        If the user is an admin the diagram owner field can be set to any user,
        otherwise owner is set to the authenticated user.
        """
        if self.request.user.is_admin:
            owner_id = self.request.data.get("owner")
            owner = (
                get_user_model().objects.get(id=owner_id)
                if owner_id
                else self.request.user
            )
            serializer.save(owner=owner)
        else:
            super().perform_update(serializer)


# region @extend_schema
@extend_schema(
    tags=[DiagramsConfig.tag],
    summary="Create a copy of an existing diagram",
    description="This API endpoint allows you to create a copy of an existing diagram. "
    "Copied diagram will have the same content as the original one, \
    but a different title. New diagram description can be provided. \
    The owner of the copied diagram will be the authenticated user.",
    responses={
        201: DiagramCopySerializer,
        400: OpenApiResponse(description="Bad request"),
        404: OpenApiResponse(description="Diagram not found"),
    },
)
# endregion
class DiagramCopyAPIView(generics.CreateAPIView):
    """
    API endpoint that allows to create a copy of an existing diagram.
    """

    queryset: QuerySet[Diagram] = Diagram.objects.all()
    serializer_class = DiagramCopySerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsOwner]

    def perform_create(self, serializer: DiagramCopySerializer) -> None:
        original_diagram = self.get_object()
        serializer.instance = original_diagram
        serializer.save(
            id=None,
            title=f"Copy of {original_diagram.title}",
            created_at=timezone.now(),
            updated_at=timezone.now(),
            owner=self.request.user,
        )
