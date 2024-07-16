from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrIsOwner(permissions.BasePermission):
    """
    Custom permission which allows:
    - admins to do anything with any objects;
    - other users to view or edit just their own objects.
    """

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        if request.user.is_admin:
            return True
        return obj.owner == request.user
