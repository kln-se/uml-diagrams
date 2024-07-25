from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.diagrams.api.v1.permissions import IsAdminOrIsOwner
from apps.users.constants import UserRoles
from tests.factories import DiagramFactory, UserFactory


def test_is_admin_or_is_owner_permission_granted_for_owner() -> None:
    """
    GIVEN a user who owns the diagram
    WHEN the permission is checked for the user
    THEN the permission is granted
    """
    permission = IsAdminOrIsOwner()
    request = APIRequestFactory().get("/")
    user = UserFactory(role=UserRoles.USER)
    request.user = user
    diagram_owned_by_user = DiagramFactory(owner=user)
    assert permission.has_object_permission(request, APIView(), diagram_owned_by_user)


def test_is_admin_or_is_owner_permission_not_granted_for_not_owner() -> None:
    """
    GIVEN a user who NOT owns the diagram and another user who owns the diagram
    WHEN the permission is checked for the user
    THEN the permission is not granted
    """
    permission = IsAdminOrIsOwner()
    request = APIRequestFactory().get("/")
    user = UserFactory(role=UserRoles.USER)
    request.user = user
    diagram_owned_by_another_user = DiagramFactory()
    assert not permission.has_object_permission(
        request, APIView(), diagram_owned_by_another_user
    )


def test_is_admin_or_is_owner_permission_granted_for_admin() -> None:
    """
    GIVEN an admin and a user who owns the diagram
    WHEN the permission is checked for the admin
    THEN the permission is granted
    """
    permission = IsAdminOrIsOwner()
    request = APIRequestFactory().get("/")
    admin = UserFactory(role=UserRoles.ADMIN)
    request.user = admin
    diagram_owned_by_another_user = DiagramFactory()
    assert permission.has_object_permission(
        request, APIView(), diagram_owned_by_another_user
    )
