import pytest
from django.http.response import Http404
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory

from apps.diagrams.api.v1.pagination import DiagramViewSetPagination
from apps.diagrams.api.v1.permissions import IsAdminOrIsOwner
from apps.diagrams.api.v1.serializers import (
    DiagramCopySerializer,
    DiagramListSerializer,
    DiagramSerializer,
)
from apps.diagrams.api.v1.views import DiagramCopyAPIView, DiagramViewSet
from apps.users.constants import UserRoles
from tests.factories import DiagramFactory, UserFactory


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
        request.data = {"owner": another_user.id}
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
        request.data = {"owner": admin.id}
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
            "owner": another_user.id,
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
            "owner": another_user.id,
        }
        viewset = DiagramViewSet(request=request)
        serializer = DiagramSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        viewset.perform_create(serializer)
        assert serializer.instance.owner == another_user

    @pytest.mark.parametrize(
        ("action", "serializer_class"),
        [("list", DiagramListSerializer), ("retrieve", DiagramSerializer)],
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


class TestDiagramCopyAPIView:
    def test_perform_create_correct(self) -> None:
        """
        GIVEN a diagram
        WHEN perform_create() is called
        THEN check that the copy of the diagram is created.
        """
        user = UserFactory(role=UserRoles.USER)
        original_diagram = DiagramFactory(owner=user)
        request = APIRequestFactory()
        request.user = user
        viewset = DiagramCopyAPIView(
            request=request, kwargs={"pk": original_diagram.id}
        )
        serializer = DiagramCopySerializer(
            original_diagram, data={"description": "Copied."}, partial=True
        )
        serializer.is_valid()
        viewset.perform_create(serializer)
        assert serializer.instance != original_diagram
        assert serializer.instance.title == f"Copy of {original_diagram.title}"
        assert serializer.instance.description != original_diagram.description
        assert serializer.instance.owner == user
        assert serializer.instance.id != original_diagram.id
        assert serializer.instance.created_at != original_diagram.created_at
        assert serializer.instance.updated_at != original_diagram.updated_at

    def test_permission_class_correct(self) -> None:
        viewset = DiagramCopyAPIView()
        assert viewset.permission_classes == [IsAuthenticated, IsAdminOrIsOwner]
