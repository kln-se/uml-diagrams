from typing import Union

import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.sharings.api.v1.permissions import (
    IsAdminOrIsSharingOwner,
    IsCollaborator,
    IsCollaboratorAndHasViewCopyPermission,
    IsCollaboratorAndHasViewEditPermission,
    IsPublicDiagram,
)
from apps.sharings.constants import PermissionLevels
from apps.users.constants import UserRoles
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory, UserFactory


class TestIsAdminOrIsSharingOwner:
    def test_is_admin_or_is_sharing_owner_permission_succeeded_for_owner(self) -> None:
        """
        GIVEN a user who owns the diagram and share it to another user
        WHEN the permission is checked for the owner of sharing invitation
        THEN the permission is granted.
        """
        permission = IsAdminOrIsSharingOwner()
        request = APIRequestFactory().get("/")
        owner = UserFactory(role=UserRoles.USER)
        request.user = owner
        diagram_owned_by_user = DiagramFactory(owner=owner)
        # sharing invitation presented in database as collaborator record
        collaborator = CollaboratorFactory(
            diagram=diagram_owned_by_user, shared_to=UserFactory()
        )
        assert permission.has_object_permission(request, APIView(), collaborator)

    def test_is_admin_or_is_sharing_owner_permission_failed_for_not_owner(self) -> None:
        """
        GIVEN a user who NOT owns the diagram and another user who owns the diagram \
        and share it to another user
        WHEN the permission is checked for the user who not owns the diagram to get \
        access to this sharing invitation
        THEN the permission is not granted.
        """
        permission = IsAdminOrIsSharingOwner()
        request = APIRequestFactory().get("/")
        not_owner = UserFactory(role=UserRoles.USER)
        request.user = not_owner
        diagram_owned_by_another_user = DiagramFactory()
        collaborator = CollaboratorFactory(
            diagram=diagram_owned_by_another_user, shared_to=UserFactory()
        )
        assert not permission.has_object_permission(request, APIView(), collaborator)

    def test_is_admin_or_is_sharing_owner_permission_succeeded_for_admin(self) -> None:
        """
        GIVEN an admin and a user who owns the diagram and share it to another user
        WHEN the permission is checked for the admin to get \
        access to this sharing invitation
        THEN the permission is granted.
        """
        permission = IsAdminOrIsSharingOwner()
        request = APIRequestFactory().get("/")
        admin = UserFactory(role=UserRoles.ADMIN)
        request.user = admin
        diagram_owned_by_another_user = DiagramFactory()
        collaborator = CollaboratorFactory(
            diagram=diagram_owned_by_another_user, shared_to=UserFactory()
        )
        assert permission.has_object_permission(request, APIView(), collaborator)


class TestIsCollaborator:
    def test_is_collaborator_permission_succeeded_for_collaborator(self) -> None:
        """
        GIVEN a user who was invited to the diagram as collaborator by its owner
        WHEN the permission is checked for this user
        THEN the permission is granted.
        """
        permission = IsCollaborator()
        request = APIRequestFactory().get("/")
        collaborator = CollaboratorFactory()
        request.user = collaborator.shared_to
        assert permission.has_object_permission(
            request, APIView(), collaborator.diagram
        )

    def test_is_collaborator_permission_failed_for_not_collaborator(self) -> None:
        """
        GIVEN a user who was not invited to the diagram as collaborator but
        tries to get access to the diagram
        WHEN the permission is checked for this user
        THEN the permission is not granted.
        """
        permission = IsCollaborator()
        request = APIRequestFactory().get("/")
        not_collaborator = UserFactory(role=UserRoles.USER)
        request.user = not_collaborator
        diagram = DiagramFactory()
        assert not permission.has_object_permission(request, APIView(), diagram)


class TestIsCollaboratorAndHasViewCopyPermission:
    def test_is_collaborator_and_has_view_copy_permission_user_granted_valid_permission(
        self,
    ) -> None:
        """
        GIVEN a user who was invited to the diagram as collaborator by its owner
        with valid "view-copy" permission
        WHEN the permission is checked for this user
        THEN the permission is granted.
        """
        permission = IsCollaboratorAndHasViewCopyPermission()
        request = APIRequestFactory().get("/")
        collaborator = CollaboratorFactory(permission_level=PermissionLevels.VIEWCOPY)
        request.user = collaborator.shared_to
        assert permission.has_object_permission(
            request, APIView(), collaborator.diagram
        )

    def test_is_collaborator_and_has_view_copy_permission_granted_invalid_permission(
        self,
    ) -> None:
        """
        GIVEN a user who was invited to the diagram as collaborator by its owner
        with invalid "view-only" permission
        WHEN the permission is checked for this user
        THEN the permission is not granted.
        """
        permission = IsCollaboratorAndHasViewEditPermission()
        request = APIRequestFactory().get("/")
        collaborator = CollaboratorFactory(permission_level=PermissionLevels.VIEWONLY)
        request.user = collaborator.shared_to
        assert not permission.has_object_permission(
            request, APIView(), collaborator.diagram
        )

    def test_is_collaborator_and_has_view_copy_permission_failed_for_not_collaborator(
        self,
    ) -> None:
        """
        GIVEN a user who was not invited to the diagram as collaborator but
        tries to get access to the diagram
        WHEN the permission is checked for this user
        THEN the permission is not granted.
        """
        permission = IsCollaboratorAndHasViewCopyPermission()
        request = APIRequestFactory().get("/")
        not_collaborator = UserFactory(role=UserRoles.USER)
        request.user = not_collaborator
        diagram = DiagramFactory()
        assert not permission.has_object_permission(request, APIView(), diagram)


class TestIsCollaboratorAndHasViewEditPermission:
    def test_is_collaborator_and_has_view_edit_permission_user_granted_valid_permission(
        self,
    ) -> None:
        """
        GIVEN a user who was invited to the diagram as collaborator by its owner
        with valid "view-edit" permission
        WHEN the permission is checked for this user
        THEN the permission is granted.
        """
        permission = IsCollaboratorAndHasViewEditPermission()
        request = APIRequestFactory().get("/")
        collaborator = CollaboratorFactory(permission_level=PermissionLevels.VIEWEDIT)
        request.user = collaborator.shared_to
        assert permission.has_object_permission(
            request, APIView(), collaborator.diagram
        )

    def test_is_collaborator_and_has_view_edit_permission_granted_invalid_permission(
        self,
    ) -> None:
        """
        GIVEN a user who was invited to the diagram as collaborator by its owner
        with invalid "view-only" permission
        WHEN the permission is checked for this user
        THEN the permission is not granted.
        """
        permission = IsCollaboratorAndHasViewEditPermission()
        request = APIRequestFactory().get("/")
        collaborator = CollaboratorFactory(permission_level=PermissionLevels.VIEWONLY)
        request.user = collaborator.shared_to
        assert not permission.has_object_permission(
            request, APIView(), collaborator.diagram
        )

    def test_is_collaborator_and_has_view_edit_permission_failed_for_not_collaborator(
        self,
    ) -> None:
        """
        GIVEN a user who was not invited to the diagram as collaborator but
        tries to get access to the diagram
        WHEN the permission is checked for this user
        THEN the permission is not granted.
        """
        permission = IsCollaboratorAndHasViewEditPermission()
        request = APIRequestFactory().get("/")
        not_collaborator = UserFactory(role=UserRoles.USER)
        request.user = not_collaborator
        diagram = DiagramFactory()
        assert not permission.has_object_permission(request, APIView(), diagram)


class TestIsPublicDiagramPermission:
    @pytest.mark.parametrize(
        "user",
        [
            AnonymousUser,
            UserFactory,
        ],
    )
    def test_is_public_diagram_permission_for_any_user_type_is_granted(
        self, user: Union[AnonymousUser, User]
    ) -> None:
        """
        GIVEN a user who tries to get access to the public diagram
        WHEN is checked that the diagram meets the public sharing requirements
        THEN the permission is granted.
        """
        permission = IsPublicDiagram()
        request = APIRequestFactory().get("/")
        public_diagram_sharing = CollaboratorFactory(
            shared_to=None,
            permission_level=PermissionLevels.VIEWONLY,
        )
        request.user = user()
        assert permission.has_object_permission(
            request, APIView(), public_diagram_sharing.diagram
        )

    @pytest.mark.parametrize(
        "user",
        [
            AnonymousUser,
            UserFactory,
        ],
    )
    def test_is_public_diagram_permission_for_not_public_diagram_is_not_granted(
        self, user: Union[AnonymousUser, User]
    ) -> None:
        """
        GIVEN a user who tries to get access to the not public diagram
        WHEN is checked if the diagram meets the requirements
        THEN the permission is not granted to access the diagram.
        """
        permission = IsPublicDiagram()
        request = APIRequestFactory().get("/")
        personal_sharing = CollaboratorFactory()
        request.user = user()
        assert not permission.has_object_permission(
            request, APIView(), personal_sharing.diagram
        )
