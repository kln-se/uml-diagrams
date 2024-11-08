from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.diagrams.models import Diagram
from apps.sharings.constants import PermissionLevels
from apps.sharings.models import Collaborator


class IsAdminOrIsSharingOwner(permissions.BasePermission):
    """
    Custom permission which allows:
    - admins to do anything with any share invitation (collaborator obj.;
    - other users to view or edit just their own share invitation.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Collaborator
    ) -> bool:
        if request.user.is_admin:
            return True
        return obj.diagram.owner == request.user


class IsCollaborator(permissions.BasePermission):
    """
    Custom permission which allows user to access the diagram
    if he is the one who the diagram was shared to (i.e. collaborator).
    Permission "view-only" is required in database.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Diagram
    ) -> bool:
        return Collaborator.objects.filter(diagram=obj, shared_to=request.user).exists()


class IsCollaboratorAndHasViewCopyPermission(permissions.BasePermission):
    """
    Custom permission which allows collaborator to copy shared diagram
    if he has the appropriate permission.
    Permission "view-copy" is required in database.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Diagram
    ) -> bool:
        return Collaborator.objects.filter(
            diagram=obj,
            shared_to=request.user,
            permission_level=PermissionLevels.VIEWCOPY,
        ).exists()


class IsCollaboratorAndHasViewEditPermission(permissions.BasePermission):
    """
    Custom permission which allows collaborator to edit shared diagram
    and save changes to it if he has the appropriate permission.
    Permission "view-edit" is required in database.
    """

    def has_object_permission(
        self, request: Request, view: APIView, obj: Diagram
    ) -> bool:
        return Collaborator.objects.filter(
            diagram=obj,
            shared_to=request.user,
            permission_level=PermissionLevels.VIEWEDIT,
        ).exists()
