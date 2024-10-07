from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import filters, generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.diagrams.api.v1.pagination import DiagramViewSetPagination
from apps.diagrams.api.v1.permissions import IsAdminOrIsOwner
from apps.diagrams.api.v1.serializers import (
    DiagramCopySerializer,
    DiagramListSerializer,
    DiagramSerializer,
)
from apps.diagrams.apps import DiagramsConfig
from apps.diagrams.models import Diagram
from apps.sharings.api.v1.actions import invite_collaborator, remove_all_collaborators
from apps.sharings.api.v1.permissions import IsCollaborator
from apps.sharings.api.v1.serializers import InviteCollaboratorSerializer
from apps.sharings.models import Collaborator
from docs.api.templates.parameters import required_header_auth_parameter


# region @extend_schema
@extend_schema_view(
    list=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="List diagrams",
        description="Returns a list of all available diagrams.",
        parameters=[required_header_auth_parameter],
        responses={
            200: DiagramListSerializer(many=True),
            401: OpenApiResponse(description="Invalid token or token not provided"),
        },
    ),
    create=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Create a new diagram",
        description="Creates a new diagram based on the provided data.",
        parameters=[required_header_auth_parameter],
        responses={
            200: DiagramSerializer,
            400: OpenApiResponse(description="JSON parse error"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
        },
    ),
    retrieve=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Retrieve a diagram",
        description="Returns the details of a specific diagram.",
        parameters=[required_header_auth_parameter],
        responses={
            200: DiagramSerializer,
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Diagram not found"),
        },
    ),
    update=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Update a diagram",
        description="Updates the details of a specific diagram.",
        parameters=[required_header_auth_parameter],
        responses={
            200: DiagramSerializer,
            400: OpenApiResponse(description="JSON parse error"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Diagram not found"),
        },
    ),
    partial_update=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Partially update a diagram",
        description="Partially updates the details of a specific diagram.",
        parameters=[required_header_auth_parameter],
        responses={
            200: DiagramSerializer,
            400: OpenApiResponse(description="JSON parse error"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Diagram not found"),
        },
    ),
    destroy=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Delete a diagram",
        description="Deletes a specific diagram.",
        parameters=[required_header_auth_parameter],
        responses={
            204: OpenApiResponse(description="Deleted successfully"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Diagram not found"),
        },
    ),
    invite_collaborator=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Invite a collaborator to a diagram",
        description="A diagram owner can share his diagram to another user using "
        "its email and provide one of the following permission levels:\n"
        "- *view-only*: user can only view shared diagram;\n"
        "- *view-copy*: user can view and copy shared diagram "
        "to his/her own account;\n"
        "- *view-edit*: user can view, copy, and edit shared diagram.\n\n"
        "**Admin can share any diagram**.",
        parameters=[required_header_auth_parameter],
        responses={
            200: InviteCollaboratorSerializer,
            400: OpenApiResponse(
                description="Possible errors:\n"
                "- JSON parse error;\n"
                "- invalid email provided;\n"
                "- invalid permission level provided;\n"
                "- self-sharing is not allowed;\n"
                "- sharing the same diagram to the same user is not allowed."
            ),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Diagram not found"),
        },
    ),
    remove_all_collaborators=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Remove all collaborators from a diagram",
        description="Removes all users which diagram was shared to "
        "from the collaborators list of a provided diagram.",
        parameters=[required_header_auth_parameter],
        responses={
            204: OpenApiResponse(description="Removed successfully"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Diagram not found"),
        },
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
    pagination_class = DiagramViewSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["title", "owner_email", "created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self) -> QuerySet[Diagram]:
        """
        Filter the queryset based on the user's permissions:
        - if the user is an admin, return all diagrams;
        - otherwise, return only the diagrams that belong to the user.
        """
        if self.request.user.is_admin:
            return Diagram.objects.all()
        return self.queryset.filter(owner=self.request.user)

    def perform_update(self, serializer: DiagramSerializer) -> None:
        """
        If the user has admin permissions,
        the diagram owner_id field can be set to any user,
        otherwise owner_id field is remained unchanged.
        """
        owner = serializer.instance.owner
        if self.request.data.get("owner_id") and self.request.user.is_admin:
            owner = get_user_model().objects.get(id=self.request.data.get("owner_id"))
        serializer.save(owner_id=owner.id)

    def perform_create(self, serializer: DiagramSerializer) -> None:
        """
        If the user has admin permissions,
        the diagram owner_id field can be set to any user,
        otherwise owner_id field is remained unchanged.
        """
        owner = self.request.user
        if self.request.data.get("owner_id") and self.request.user.is_admin:
            owner = get_user_model().objects.get(id=self.request.data.get("owner_id"))
        serializer.save(owner_id=owner.id)

    def get_serializer_class(self):
        serializer_mapping = {
            "list": DiagramListSerializer,
            "invite_collaborator": InviteCollaboratorSerializer,
            "remove_all_collaborators": None,
        }
        return serializer_mapping.get(self.action, super().get_serializer_class())

    @action(detail=True, methods=["post"], url_path="share-invite-user")
    def invite_collaborator(self, *args, **kwargs):
        """
        Allows owner to share his diagram to another user using its email.
        Admin can share any diagram.
        """
        return invite_collaborator(self, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="share-unshare-all")
    def remove_all_collaborators(self, *args, **kwargs):
        """
        Allows owner to remove all collaborators from his diagram.
        """
        return remove_all_collaborators(self, *args, **kwargs)


# region @extend_schema
@extend_schema(
    tags=[DiagramsConfig.tag],
    summary="Create a copy of an existing diagram",
    description="Allows user to create a copy of their own diagram.\n\n"
    "Features:\n"
    "- copied diagram will have the same content as the original one, "
    "but a different title: `Copy of {original_diagram_title}`;\n"
    "- new diagram description can be provided optionally;\n"
    "- the owner of the copied diagram will be the authenticated user.\n\n"
    "**Admin user can copy any diagram.**\n\n"
    "Parameter **id** should be provided **with minus sign** "
    "in the following UUID format: `123e4567-e89b-12d3-a456-426614174000`.",
    parameters=[required_header_auth_parameter],
    responses={
        201: DiagramCopySerializer,
        400: OpenApiResponse(description="JSON parse error"),
        401: OpenApiResponse(description="Invalid token or token not provided"),
        403: OpenApiResponse(description="Forbidden to copy this diagram"),
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
            owner=self.request.user,
        )


# region @extend_schema
@extend_schema_view(
    list=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="List diagrams shared to the current user",
        description="Returns a list of all diagrams shared to the current user "
        "by another users.",
        parameters=[required_header_auth_parameter],
        responses={
            200: DiagramListSerializer(many=True),
            401: OpenApiResponse(description="Invalid token or token not provided"),
        },
    ),
    retrieve=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Retrieve a diagram shared to the current user",
        description="Returns the details of a specific diagram shared to the "
        "current user by another user.",
        parameters=[required_header_auth_parameter],
        responses={
            200: DiagramSerializer,
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Shared diagram not found"),
        },
    ),
)
# endregion
class SharedWithMeDiagramViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    """
    API endpoint that allows:
    - view list of all diagrams which were shared to the current user;
    - view a diagram that was shared to the current user.
    """

    queryset: QuerySet[Diagram] = Diagram.objects.all()
    serializer_class = DiagramSerializer
    permission_classes = [IsAuthenticated, IsCollaborator]
    http_method_names = ["get"]
    pagination_class = DiagramViewSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["title", "owner_email", "created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self) -> QuerySet[Diagram]:
        """
        Filter the queryset to return only the diagrams which were shared
        to the current user.
        """
        shared_diagrams_id = Collaborator.objects.filter(
            shared_to=self.request.user
        ).values("diagram_id")
        return Diagram.objects.filter(id__in=shared_diagrams_id)

    def get_serializer_class(self):
        serializer_mapping = {
            "list": DiagramListSerializer,
            "retrieve": DiagramSerializer,
        }
        return serializer_mapping.get(self.action, super().get_serializer_class())
