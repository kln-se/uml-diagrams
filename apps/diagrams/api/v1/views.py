from django.db.models import QuerySet
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, viewsets

from apps.diagrams.api.v1.serializers import DiagramCopySerializer, DiagramSerializer
from apps.diagrams.models import Diagram


@extend_schema_view(
    list=extend_schema(
        summary="List diagrams", description="Returns a list of all available diagrams."
    ),
    create=extend_schema(
        summary="Create a new diagram",
        description="Creates a new diagram based on the provided data.",
        request=DiagramSerializer,
        responses={201: DiagramSerializer},
    ),
    retrieve=extend_schema(
        summary="Retrieve a diagram",
        description="Returns the details of a specific diagram.",
        responses={200: DiagramSerializer},
    ),
    update=extend_schema(
        summary="Update a diagram",
        description="Updates the details of a specific diagram.",
        request=DiagramSerializer,
        responses={200: DiagramSerializer},
    ),
    partial_update=extend_schema(
        summary="Partially update a diagram",
        description="Partially updates the details of a specific diagram.",
        request=DiagramSerializer,
        responses={200: DiagramSerializer},
    ),
    destroy=extend_schema(
        summary="Delete a diagram",
        description="Deletes a specific diagram.",
        responses={204: None},
    ),
)
class DiagramViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows:
    - view all diagrams;
    - store a new diagram;
    - view, edit or delete an existing diagram.
    """

    queryset: QuerySet[Diagram] = Diagram.objects.all()
    serializer_class = DiagramSerializer


@extend_schema(
    summary="Create a copy of an existing diagram",
    description="This API endpoint allows you to create a copy of an existing diagram. "
    "Copied diagram will have the same content as the original one, \
    but a different title.",
    responses={
        201: OpenApiResponse(description="Created", response=DiagramCopySerializer),
        400: OpenApiResponse(description="Bad request"),
        404: OpenApiResponse(description="Not found"),
    },
)
class DiagramCopyAPIView(generics.CreateAPIView):
    """
    API endpoint that allows to create a copy of an existing diagram.
    """

    queryset: QuerySet[Diagram] = Diagram.objects.all()
    serializer_class = DiagramCopySerializer

    def perform_create(self, serializer: DiagramCopySerializer) -> None:
        original_diagram = self.get_object()
        serializer.instance = original_diagram
        serializer.save(
            id=None,
            title=f"Copy of {original_diagram.title}",
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
