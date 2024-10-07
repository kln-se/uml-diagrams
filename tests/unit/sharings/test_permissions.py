from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.sharings.api.v1.permissions import IsAdminOrIsOwner, IsCollaborator
from apps.users.constants import UserRoles
from tests.factories import CollaboratorFactory, DiagramFactory, UserFactory


def test_is_admin_or_is_owner_permission_granted_for_owner() -> None:
    """
    GIVEN a user who owns the diagram and share it to another user
    WHEN the permission is checked for the owner of sharing invitation
    THEN the permission is granted
    """
    permission = IsAdminOrIsOwner()
    request = APIRequestFactory().get("/")
    owner = UserFactory(role=UserRoles.USER)
    request.user = owner
    diagram_owned_by_user = DiagramFactory(owner=owner)
    collaborator = CollaboratorFactory(
        diagram=diagram_owned_by_user, shared_to=UserFactory()
    )
    assert permission.has_object_permission(request, APIView(), collaborator)


def test_is_admin_or_is_owner_permission_not_granted_for_not_owner() -> None:
    """
    GIVEN a user who NOT owns the diagram and another user who owns the diagram \
    and share it to another user
    WHEN the permission is checked for the user who not owns the diagram to get \
    access to this sharing invitation
    THEN the permission is not granted
    """
    permission = IsAdminOrIsOwner()
    request = APIRequestFactory().get("/")
    not_owner = UserFactory(role=UserRoles.USER)
    request.user = not_owner
    diagram_owned_by_another_user = DiagramFactory()
    collaborator = CollaboratorFactory(
        diagram=diagram_owned_by_another_user, shared_to=UserFactory()
    )
    assert not permission.has_object_permission(request, APIView(), collaborator)


def test_is_admin_or_is_owner_permission_granted_for_admin() -> None:
    """
    GIVEN an admin and a user who owns the diagram and share it to another user
    WHEN the permission is checked for the admin to get \
    access to this sharing invitation
    THEN the permission is granted
    """
    permission = IsAdminOrIsOwner()
    request = APIRequestFactory().get("/")
    admin = UserFactory(role=UserRoles.ADMIN)
    request.user = admin
    diagram_owned_by_another_user = DiagramFactory()
    collaborator = CollaboratorFactory(
        diagram=diagram_owned_by_another_user, shared_to=UserFactory()
    )
    assert permission.has_object_permission(request, APIView(), collaborator)


def test_is_collaborator_permission_granted_for_collaborator() -> None:
    """
    GIVEN a user who was invited to the diagram as collaborator by its owner
    WHEN the permission is checked for this user
    THEN the permission is granted
    """
    permission = IsCollaborator()
    request = APIRequestFactory().get("/")
    owner, collaborator = UserFactory(role=UserRoles.USER), UserFactory(
        role=UserRoles.USER
    )
    request.user = collaborator
    diagram = DiagramFactory(owner=owner)
    # create sharing invitation
    _ = CollaboratorFactory(diagram=diagram, shared_to=collaborator)
    assert permission.has_object_permission(request, APIView(), diagram)


def test_is_collaborator_permission_not_granted_for_not_collaborator() -> None:
    """
    GIVEN a user who was not invited to the diagram as collaborator but
    tries to get access to the diagram
    WHEN the permission is checked for this user
    THEN the permission is not granted
    """
    permission = IsCollaborator()
    request = APIRequestFactory().get("/")
    owner, some_other_user = UserFactory(role=UserRoles.USER), UserFactory(
        role=UserRoles.USER
    )
    request.user = some_other_user
    diagram = DiagramFactory(owner=owner)
    # create sharing invitation
    _ = CollaboratorFactory(
        diagram=DiagramFactory(owner=owner), shared_to=UserFactory(role=UserRoles.USER)
    )
    assert not permission.has_object_permission(request, APIView(), diagram)
