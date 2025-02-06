from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, QuerySet, Subquery
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.diagrams.api.v1.actions import copy_diagram, save_diagram, unshare_me
from apps.diagrams.api.v1.pagination import DiagramViewSetPagination
from apps.diagrams.api.v1.permissions import IsAdminOrIsDiagramOwner
from apps.diagrams.api.v1.serializers import (
    DiagramCopySerializer,
    DiagramListSerializerWithPublicFlag,
    DiagramSerializer,
    SharedDiagramListSerializer,
    SharedDiagramSaveSerializer,
)
from apps.diagrams.apps import DiagramsConfig
from apps.diagrams.models import Diagram
from apps.sharings.api.v1.actions import (
    invite_collaborator,
    remove_all_collaborators,
    set_diagram_private,
    set_diagram_public,
)
from apps.sharings.api.v1.permissions import (
    IsCollaborator,
    IsCollaboratorAndHasViewCopyPermission,
    IsCollaboratorAndHasViewEditPermission,
    IsPublicDiagram,
)
from apps.sharings.api.v1.serializers import (
    InviteCollaboratorSerializer,
    PublicDiagramSharingSerializer,
)
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
            200: DiagramListSerializerWithPublicFlag(many=True),
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
    copy_diagram=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Create a copy of an existing diagram",
        description="Allows user to create a copy of their own diagram.\n\n"
        "Features:\n"
        "- copied diagram will have the same content as the original one, "
        "but a different title: `Copy of {original_diagram_title}`;\n"
        "- new diagram description can be provided optionally;\n"
        "- the owner of the copied diagram will be the authenticated user.\n\n"
        "**Admin user can copy any diagram.**",
        parameters=[required_header_auth_parameter],
        responses={
            201: DiagramCopySerializer,
            400: OpenApiResponse(description="JSON parse error"),
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
            201: InviteCollaboratorSerializer,
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
    set_diagram_public=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Make a diagram shared as public",
        description="A diagram owner can share his diagram publicly.\n\n"
        "It will be accessible to anyone who knows the **diagram ID** by "
        "`api/v1/diagrams/public/{diagram_id}/` endpoint.",
        parameters=[required_header_auth_parameter],
        request=None,
        responses={
            201: OpenApiResponse(description="Diagram shared as public successfully"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Diagram not found"),
        },
    ),
    set_diagram_private=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Make a publicly shared diagram private again",
        description="A diagram owner can make his diagram private again, if it was "
        "shared as public before.\n\n"
        "It will become accessible only by the diagram owner and its collaborators.",
        parameters=[required_header_auth_parameter],
        request=None,
        responses={
            204: OpenApiResponse(description="Diagram become private successfully"),
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
    permission_classes = [IsAuthenticated, IsAdminOrIsDiagramOwner]
    pagination_class = DiagramViewSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["title", "owner_email", "created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self) -> QuerySet[Diagram]:
        """
        Filter the queryset based on the user's permissions:
        - if the user is an admin, return all diagrams;
        - otherwise, return only the diagrams that belong to the user.
        Each diagram object is annotated with value of whether it is public or not.
        It will help to share diagram as public
        without having to make unnecessary intermediate requests.
        """
        if self.request.user.is_admin:
            return Diagram.objects.all()
        diagrams = self.queryset.filter(owner=self.request.user)
        return diagrams.annotate(
            is_public=Exists(
                Collaborator.objects.filter(diagram_id=OuterRef("id"), shared_to=None)
            )
        )

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
            "list": DiagramListSerializerWithPublicFlag,
            "copy_diagram": DiagramCopySerializer,
            "invite_collaborator": InviteCollaboratorSerializer,
            "remove_all_collaborators": None,
            "set_diagram_public": PublicDiagramSharingSerializer,
        }
        return serializer_mapping.get(self.action, super().get_serializer_class())

    @action(detail=True, methods=["post"], url_path="copy")
    def copy_diagram(self, *args, **kwargs):
        """
        Allows diagram owner or admin to create a copy of an existing diagram.
        """
        return copy_diagram(self, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="share-invite-user")
    def invite_collaborator(self, *args, **kwargs):
        """
        Allows diagram owner to share his diagram to another user using its email.
        Admin can share any diagram.
        """
        return invite_collaborator(self, *args, **kwargs)

    @action(detail=True, methods=["delete"], url_path="share-unshare-all")
    def remove_all_collaborators(self, *args, **kwargs):
        """
        Allows diagram owner to remove all collaborators from his diagram.
        """
        return remove_all_collaborators(self, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="share-set-public")
    def set_diagram_public(self, *args, **kwargs):
        """
        Allows diagram owner to make a diagram public i.e. share it publicly.
        Any user can view public diagrams.
        """
        return set_diagram_public(self, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="share-set-private")
    def set_diagram_private(self, *args, **kwargs):
        """
        Allows diagram owner to make publicly shared diagram private.
        """
        return set_diagram_private(self, *args, **kwargs)


# region @extend_schema
@extend_schema_view(
    list=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="List diagrams shared to the current user",
        description="Returns a list of all diagrams shared to the current user "
        "by another users.",
        parameters=[required_header_auth_parameter],
        responses={
            200: SharedDiagramListSerializer(many=True),
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
    copy_shared_diagram=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Copy a diagram shared to the current user",
        description="Allows to copy a specific diagram shared to the current "
        "user to the user's account, if its owner shared it to him with "
        "**view-copy** (View & Copy) or **view-edit** (View & Edit) permission.",
        parameters=[required_header_auth_parameter],
        responses={
            201: DiagramCopySerializer,
            400: OpenApiResponse(description="Possible errors:\n- JSON parse error."),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            403: OpenApiResponse(
                description="Insufficient permission to copy diagram to user's account"
            ),
            404: OpenApiResponse(description="Shared diagram not found"),
        },
    ),
    save_shared_diagram=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Save changes made to the shared diagram",
        description="Allows to save changes made to a specific "
        "diagram shared to the current user, "
        "if its owner shared it to him with **view-edit** "
        "(View & Edit) permission.",
        parameters=[required_header_auth_parameter],
        responses={
            200: SharedDiagramSaveSerializer,
            400: OpenApiResponse(description="Possible errors:\n- JSON parse error."),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            403: OpenApiResponse(
                description="Insufficient permission to save made changes"
            ),
            404: OpenApiResponse(description="Shared diagram not found"),
        },
    ),
    unshare_me_from_diagram=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Unsubscribe user from a shared diagram",
        description="Allows logged-in user to unsubscribe himself from "
        "the diagram if it was shared to him. "
        "Unsubscribed user will be removed from diagram collaborators list.",
        parameters=[required_header_auth_parameter],
        responses={
            204: OpenApiResponse(description="Removed successfully"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Diagram not found"),
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
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = DiagramViewSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["title", "owner_email", "created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self) -> QuerySet[Diagram]:
        """
        Filter the queryset to return only the diagrams which were shared
        to the current user. Each shared diagram object is annotated with value
        of the permission level it was shared with.
        """
        shared_diagrams_id = Collaborator.objects.filter(
            shared_to=self.request.user
        ).values("diagram_id")
        return Diagram.objects.filter(id__in=shared_diagrams_id).annotate(
            permission_level=Subquery(
                Collaborator.objects.filter(
                    shared_to_id=self.request.user.id, diagram_id=OuterRef("id")
                ).values("permission_level")
            )
        )

    def get_serializer_class(self):
        serializer_mapping = {
            "list": SharedDiagramListSerializer,
            "retrieve": DiagramSerializer,
            "copy_shared_diagram": DiagramCopySerializer,
            "save_shared_diagram": SharedDiagramSaveSerializer,
            "unshare_me_from_diagram": None,
        }
        return serializer_mapping.get(self.action, super().get_serializer_class())

    def get_permissions(self):
        permission_mapping = {
            "copy_shared_diagram": [
                IsAuthenticated,
                IsCollaboratorAndHasViewCopyPermission
                | IsCollaboratorAndHasViewEditPermission,
            ],
            "save_shared_diagram": [
                IsAuthenticated,
                IsCollaboratorAndHasViewEditPermission,
            ],
            "unshare_me_from_diagram": [IsAuthenticated, IsCollaborator],
        }
        return [
            permission()
            for permission in permission_mapping.get(
                self.action, self.permission_classes
            )
        ]

    @action(detail=True, methods=["post"], url_path="copy")
    def copy_shared_diagram(self, *args, **kwargs):
        """
        Allows invited collaborator to copy the diagram he was shared to
        if he has appropriate permission.
        Requires `IsCollaboratorAndHasViewCopyPermission` permission.
        """
        return copy_diagram(self, *args, **kwargs)

    @action(detail=True, methods=["patch"], url_path="save")
    def save_shared_diagram(self, *args, **kwargs):
        """
        Allows invited collaborator to edit and save changes to the diagram
        he was shared to if he has appropriate permission.
        Requires `IsCollaboratorAndHasViewEditPermission` permission.
        """
        return save_diagram(self, *args, **kwargs)

    @action(detail=True, methods=["delete"], url_path="unshare-me")
    def unshare_me_from_diagram(self, *args, **kwargs):
        """
        Allows user to unsubscribe himself from a shared diagram.
        Unsubscribed user will be removed from diagram collaborators.
        Requires `IsCollaborator` permission.
        """
        return unshare_me(self, *args, **kwargs)


# region @extend_schema
@extend_schema_view(
    retrieve=extend_schema(
        tags=[DiagramsConfig.tag],
        summary="Retrieve a diagram shared publicly",
        description="Returns the details of a specific diagram that was shared "
        "publicly by another user.\n\n"
        "Public diagrams are stored in the database with "
        "**shared_to** field set to `null`.",
        parameters=[required_header_auth_parameter],
        responses={
            200: DiagramSerializer,
            404: OpenApiResponse(description="Public diagram not found"),
        },
    ),
)
# endregion
class PublicDiagramViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    """
    API endpoint that allows to view a diagram that was shared publicly.
    If a diagram was shared and 'shared_to' field is set to 'shared_to=null',
    in the database, so it will be public.
    """

    queryset: QuerySet[Diagram] = Diagram.objects.all()
    serializer_class = DiagramSerializer
    permission_classes = [AllowAny, IsPublicDiagram]

    def get_queryset(self):
        """
        Returns just diagrams that were shared publicly.
        Otherwise, if diagram is not public but its id (pk) was provided to the endpoint
        it will be processed by permission classes as if it was public.
        """
        return (
            super()
            .get_queryset()
            .filter(collaborator__isnull=False, collaborator__shared_to=None)
        )
