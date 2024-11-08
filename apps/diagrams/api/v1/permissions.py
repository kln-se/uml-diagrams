from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrIsDiagramOwner(permissions.BasePermission):
    """
    Custom permission which allows:
    - admins to do anything with any diagram;
    - other users to view or edit just their own diagrams.
    """

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        if request.user.is_admin:
            return True
        return obj.owner == request.user
