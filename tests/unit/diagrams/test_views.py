from typing import List

import pytest
from django.http.response import Http404
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework.test import APIRequestFactory

from apps.diagrams.api.v1.pagination import DiagramViewSetPagination
from apps.diagrams.api.v1.permissions import IsAdminOrIsOwner
from apps.diagrams.api.v1.serializers import (
    DiagramCopySerializer,
    DiagramListSerializer,
    DiagramSerializer,
    SharedDiagramListSerializer,
)
from apps.diagrams.api.v1.views import DiagramViewSet, SharedWithMeDiagramViewSet
from apps.sharings.api.v1.permissions import (
    IsCollaborator,
    IsCollaboratorAndHasViewCopyPermission,
)
from apps.sharings.api.v1.serializers import InviteCollaboratorSerializer
from apps.users.constants import UserRoles
from tests.factories import CollaboratorFactory, DiagramFactory, UserFactory


class TestDiagramViewSet:
    def test_get_queryset_returns_owner_diagrams_for_user(self) -> None:
        """
        GIVEN a user who owns one diagram and another user who owns another diagram
        WHEN get_queryset is called by user
        THEN check that the queryset returns the diagram that belongs to the user.
        """
        user = UserFactory(role=UserRoles.USER)
        diagram_owned_by_user, _ = DiagramFactory(owner=user), DiagramFactory()
        request = APIRequestFactory()
        request.user = user
        viewset = DiagramViewSet(request=request)
        assert viewset.get_queryset().count() == 1
        assert viewset.get_queryset().first() == diagram_owned_by_user

    def test_get_queryset_returns_all_diagrams_for_admin(self) -> None:
        """
        GIVEN an admin user
        WHEN get_queryset is called by admin
        THEN check that the queryset returns all diagrams.
        """
        admin = UserFactory(role=UserRoles.ADMIN)
        diagram_owned_by_admin, diagram_owned_by_another_user = (
            DiagramFactory(owner=admin),
            DiagramFactory(),
        )
        request = APIRequestFactory()
        request.user = admin
        viewset = DiagramViewSet(request=request)
        assert viewset.get_queryset().count() == 2
        assert list(viewset.get_queryset()) == [
            diagram_owned_by_admin,
            diagram_owned_by_another_user,
        ]

    def test_get_object_returns_owner_diagram_for_user(self) -> None:
        """
        GIVEN a user who owns one diagram
        WHEN get_object() is called by user
        THEN check that the object returns the diagram that belongs to the user.
        """
        user = UserFactory(role=UserRoles.USER)
        diagram_owned_by_user, _ = DiagramFactory(owner=user), DiagramFactory()
        request = APIRequestFactory()
        request.user = user
        request.query_params = {}
        viewset = DiagramViewSet(
            request=request, kwargs={"pk": diagram_owned_by_user.id}
        )
        assert viewset.get_object() == diagram_owned_by_user

    def test_get_object_does_not_return_other_diagram_for_user(self) -> None:
        """
        GIVEN user without diagrams and a diagram that belongs to another user
        WHEN get_object is called by user
        THEN check that the object does not return the diagram that belongs \
        to another user.
        """
        user = UserFactory(role=UserRoles.USER)
        diagram_owned_by_another_user = DiagramFactory()
        request = APIRequestFactory()
        request.user = user
        request.query_params = {}
        viewset = DiagramViewSet(
            request=request, kwargs={"pk": diagram_owned_by_another_user.id}
        )
        with pytest.raises(Http404):
            viewset.get_object()

    def test_get_object_returns_any_diagram_for_admin(self) -> None:
        """
        GIVEN an admin user
        WHEN get_object is called by admin
        THEN check that the get_object() returns any diagram.
        """
        admin = UserFactory(role=UserRoles.ADMIN)
        diagram_owned_by_admin, diagram_owned_by_another_user = (
            DiagramFactory(owner=admin),
            DiagramFactory(),
        )
        request = APIRequestFactory()
        request.user = admin
        request.query_params = {}
        viewset = DiagramViewSet(
            request=request, kwargs={"pk": diagram_owned_by_admin.id}
        )
        assert viewset.get_object() == diagram_owned_by_admin
        viewset = DiagramViewSet(
            request=request, kwargs={"pk": diagram_owned_by_another_user.id}
        )
        assert viewset.get_object() == diagram_owned_by_another_user

    def test_perform_update_user_cannot_update_owner(self) -> None:
        """
        GIVEN a user who owns a diagram and tries to set another user as owner
        WHEN perform_update() is called
        THEN check that the owner is not updated.
        """
        user, another_user = UserFactory(role=UserRoles.USER), UserFactory()
        diagram_owned_by_user = DiagramFactory(owner=user)
        request = APIRequestFactory()
        request.user = user
        request.data = {"owner_id": another_user.id}
        viewset = DiagramViewSet(
            request=request, kwargs={"pk": diagram_owned_by_user.id}
        )
        serializer = DiagramSerializer(diagram_owned_by_user, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        viewset.perform_update(serializer)
        assert serializer.instance.owner != another_user
        assert serializer.instance.owner == user

    def test_perform_update_admin_can_update_owner(self) -> None:
        """
        GIVEN an admin who tries set himself as owner of another user's diagram
        WHEN perform_update() is called
        THEN check that the owner is updated and the owner is the admin.
        """
        admin = UserFactory(role=UserRoles.ADMIN)
        diagram_owned_by_another_user = DiagramFactory()
        request = APIRequestFactory()
        request.user = admin
        request.data = {"owner_id": admin.id}
        viewset = DiagramViewSet(
            request=request, kwargs={"pk": diagram_owned_by_another_user.id}
        )
        serializer = DiagramSerializer(
            diagram_owned_by_another_user, data={}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        viewset.perform_update(serializer)
        assert serializer.instance.owner == admin

    def test_perform_create_user_cannot_set_owner_while_creating_diagram(self) -> None:
        """
        GIVEN a user who tries to set another user as owner while creating diagram
        WHEN perform_create() is called
        THEN check that the owner is set to himself.
        """
        user, another_user = UserFactory(role=UserRoles.USER), UserFactory()
        fake_diagram_data = DiagramFactory.build()
        request = APIRequestFactory()
        request.user = user
        request.data = {
            "title": fake_diagram_data.title,
            "description": fake_diagram_data.description,
            "json": fake_diagram_data.json,
            "owner_id": another_user.id,
        }
        viewset = DiagramViewSet(request=request)
        serializer = DiagramSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        viewset.perform_create(serializer)
        assert serializer.instance.owner != another_user
        assert serializer.instance.owner == user

    def test_perform_create_admin_can_set_owner_while_creating_diagram(self) -> None:
        """
        GIVEN an admn who tries to set another user as owner while creating diagram
        WHEN perform_create() is called
        THEN check that the owner is set to another user.
        """
        admin, another_user = UserFactory(role=UserRoles.ADMIN), UserFactory()
        fake_diagram_data = DiagramFactory.build()
        request = APIRequestFactory()
        request.user = admin
        request.data = {
            "title": fake_diagram_data.title,
            "description": fake_diagram_data.description,
            "json": fake_diagram_data.json,
            "owner_id": another_user.id,
        }
        viewset = DiagramViewSet(request=request)
        serializer = DiagramSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        viewset.perform_create(serializer)
        assert serializer.instance.owner == another_user

    @pytest.mark.parametrize(
        ("action", "serializer_class"),
        [
            ("list", DiagramListSerializer),
            ("retrieve", DiagramSerializer),
            ("copy_diagram", DiagramCopySerializer),
            ("invite_collaborator", InviteCollaboratorSerializer),
            ("remove_all_collaborators", None),
        ],
    )
    def test_get_serializer_class_correct(
        self, action: str, serializer_class: DiagramSerializer
    ) -> None:
        request = APIRequestFactory().get("/")
        viewset = DiagramViewSet(request=request)
        viewset.action = action
        assert viewset.get_serializer_class() == serializer_class

    def test_permission_class_correct(self) -> None:
        viewset = DiagramViewSet()
        assert viewset.permission_classes == [IsAuthenticated, IsAdminOrIsOwner]

    def test_viewset_ordering_options_correct(self) -> None:
        viewset = DiagramViewSet()
        assert viewset.filter_backends == [filters.OrderingFilter]
        assert viewset.ordering_fields == [
            "title",
            "owner_email",
            "created_at",
            "updated_at",
        ]
        assert viewset.ordering == ["-updated_at"]

    def test_viewset_pagination_class_correct(self) -> None:
        viewset = DiagramViewSet()
        assert viewset.pagination_class == DiagramViewSetPagination


class TestSharedWithMeDiagramViewSet:
    def test_get_queryset_returns_only_shared_diagrams_for_collaborator(self) -> None:
        """
        GIVEN a user who was invited to some other users diagrams as collaborator
        WHEN get_queryset is called by user
        THEN check that the queryset returns only the diagrams he was shared to.
        """
        collaborator = UserFactory(role=UserRoles.USER)
        # user was invited as collaborator to 2 different diagrams
        sharing_invitations = [
            CollaboratorFactory(shared_to=collaborator) for _ in range(2)
        ]
        # and was not invited to 1 diagram (3 invitations was made in total)
        sharing_invitations += [CollaboratorFactory()]
        request = APIRequestFactory()
        request.user = collaborator
        viewset = SharedWithMeDiagramViewSet(request=request)
        queryset = viewset.get_queryset()
        assert queryset.count() == 2
        assert sharing_invitations[0].diagram in queryset
        assert sharing_invitations[1].diagram in queryset
        assert sharing_invitations[2].diagram not in queryset

    def test_get_queryset_returns_nothing_for_non_collaborator(self) -> None:
        """
        GIVEN a user who has not invited to any diagram yet
        WHEN get_queryset is called by user
        THEN check that the queryset is empty.
        """
        collaborator = UserFactory(role=UserRoles.USER)
        request = APIRequestFactory()
        request.user = collaborator
        viewset = SharedWithMeDiagramViewSet(request=request)
        assert viewset.get_queryset().count() == 0

    @pytest.mark.parametrize(
        ("action", "serializer_class"),
        [
            ("list", SharedDiagramListSerializer),
            ("retrieve", DiagramSerializer),
            ("copy_shared_diagram", DiagramCopySerializer),
        ],
    )
    def test_get_serializer_class_correct(
        self, action: str, serializer_class: ModelSerializer
    ) -> None:
        request = APIRequestFactory().get("/")
        viewset = SharedWithMeDiagramViewSet(request=request)
        viewset.action = action
        assert viewset.get_serializer_class() == serializer_class

    def test_basic_permission_class_correct(self) -> None:
        viewset = SharedWithMeDiagramViewSet()
        assert viewset.permission_classes == [IsAuthenticated, IsCollaborator]

    @pytest.mark.parametrize(
        ("action", "permission_classes"),
        [
            ("list", [IsAuthenticated, IsCollaborator]),
            ("retrieve", [IsAuthenticated, IsCollaborator]),
            (
                "copy_shared_diagram",
                [IsAuthenticated, IsCollaboratorAndHasViewCopyPermission],
            ),
        ],
    )
    def test_get_permissions(
        self, action: str, permission_classes: List[ModelSerializer]
    ) -> None:
        request = APIRequestFactory().get("/")
        viewset = SharedWithMeDiagramViewSet(request=request)
        viewset.action = action
        for perm_obj, perm_class in zip(viewset.get_permissions(), permission_classes):
            assert isinstance(perm_obj, perm_class)

    def test_viewset_ordering_options_correct(self) -> None:
        viewset = SharedWithMeDiagramViewSet()
        assert viewset.filter_backends == [filters.OrderingFilter]
        assert viewset.ordering_fields == [
            "title",
            "owner_email",
            "created_at",
            "updated_at",
        ]
        assert viewset.ordering == ["-updated_at"]

    def test_viewset_pagination_class_correct(self) -> None:
        viewset = SharedWithMeDiagramViewSet()
        assert viewset.pagination_class == DiagramViewSetPagination

    def test_shared_with_me_diagram_viewset_http_methods_correct(self) -> None:
        viewset = SharedWithMeDiagramViewSet()
        assert viewset.http_method_names == ["get", "post"]
