import pytest
from django.http.response import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory

from apps.diagrams.api.v1.permissions import IsAdminOrIsOwner
from apps.diagrams.api.v1.serializers import DiagramCopySerializer, DiagramSerializer
from apps.diagrams.api.v1.views import DiagramCopyAPIView, DiagramViewSet
from apps.users.constants import UserRoles
from tests.factories import DiagramFactory, UserFactory


class TestDiagramViewSet:
    def test_queryset_returns_owner_diagrams_for_user(self) -> None:
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

    def test_queryset_returns_all_diagrams_for_admin(self) -> None:
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

    def test_object_returns_owner_diagram_for_user(self) -> None:
        """
        GIVEN a user who owns one diagram
        WHEN get_object is called by user
        THEN check that the object returns the diagram that belongs to the user.
        """
        user = UserFactory(role=UserRoles.USER)
        diagram_owned_by_user, _ = DiagramFactory(owner=user), DiagramFactory()
        request = APIRequestFactory()
        request.user = user
        viewset = DiagramViewSet(
            request=request, kwargs={"pk": diagram_owned_by_user.id}
        )
        assert viewset.get_object() == diagram_owned_by_user

    def test_object_does_not_return_other_diagram_for_user(self) -> None:
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
        viewset = DiagramViewSet(
            request=request, kwargs={"pk": diagram_owned_by_another_user.id}
        )
        with pytest.raises(Http404):
            viewset.get_object()

    def test_object_returns_any_diagram_for_admin(self) -> None:
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
        serializer.is_valid()
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
        serializer.is_valid()
        viewset.perform_update(serializer)
        assert serializer.instance.owner == admin

    def test_permission_class_correct(self) -> None:
        viewset = DiagramViewSet()
        assert viewset.permission_classes == [IsAuthenticated, IsAdminOrIsOwner]


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
