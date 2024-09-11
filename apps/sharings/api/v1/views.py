from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import filters, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.sharings.api.v1.pagination import SharingViewSetPagination
from apps.sharings.api.v1.permissions import IsAdminOrIsOwner
from apps.sharings.api.v1.serializers import CollaboratorSerializer
from apps.sharings.apps import SharingsConfig
from apps.sharings.models import Collaborator
from docs.api.templates.parameters import required_header_auth_parameter


# region @extend_schema
@extend_schema_view(
    list=extend_schema(
        tags=[SharingsConfig.tag],
        summary="List sharing invitations",
        description="Returns a list of all sharing invitations created by "
        "the current user.\n\n"
        "**Admin can see all sharing invitations.**",
        parameters=[required_header_auth_parameter],
        responses={
            200: CollaboratorSerializer(many=True),
            401: OpenApiResponse(description="Invalid token or token not provided"),
        },
    ),
    retrieve=extend_schema(
        tags=[SharingsConfig.tag],
        summary="Retrieve a sharing invitation",
        description="Returns the details of a specific sharing invitation.\n\n"
        "**Admin can retrieve any sharing invitations.**",
        parameters=[required_header_auth_parameter],
        responses={
            200: CollaboratorSerializer,
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Sharing not found"),
        },
    ),
    partial_update=extend_schema(
        tags=[SharingsConfig.tag],
        summary="Partially update permission level of a sharing invitation",
        description="Partially updates the permission level of a "
        "specific sharing invitation.\n\n"
        "**Admin can change permission level of any sharing invitation.**",
        parameters=[required_header_auth_parameter],
        responses={
            200: CollaboratorSerializer,
            400: OpenApiResponse(description="JSON parse error"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Sharing not found"),
        },
    ),
    destroy=extend_schema(
        tags=[SharingsConfig.tag],
        summary="Delete a sharing invitation",
        description="Deletes a specific sharing invitation.\n\n"
        "**Admin can delete any sharing invitation.**",
        parameters=[required_header_auth_parameter],
        responses={
            204: OpenApiResponse(description="Deleted successfully"),
            401: OpenApiResponse(description="Invalid token or token not provided"),
            404: OpenApiResponse(description="Sharing invitation not found"),
        },
    ),
)
# endregion
class SharingViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    API endpoint that allows:
    - view, edit (change permission level) or delete an existing sharing invitation;
    - view all sharing invitations.
    """

    queryset: QuerySet[Collaborator] = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsOwner]
    http_method_names = ["get", "patch", "delete"]
    pagination_class = SharingViewSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["diagram_id", "shared_to", "permission_level", "shared_at"]
    ordering = ["-shared_at"]

    def get_queryset(self) -> QuerySet[Collaborator]:
        """
        Filter the queryset based on the user's permissions:
        - if the user is an admin, return all sharings;
        - otherwise, return only the ones that belong to the user.
        """
        if self.request.user.is_admin:
            return Collaborator.objects.all()
        return self.queryset.filter(diagram__owner=self.request.user)
