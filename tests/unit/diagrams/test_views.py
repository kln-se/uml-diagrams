import pytest
from django.http.response import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory

from apps.diagrams.api.v1.permissions import IsAdminOrIsOwner
from apps.diagrams.api.v1.serializers import DiagramCopySerializer
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
        user, another_user = UserFactory(role=UserRoles.USER), UserFactory()
        instance, _ = DiagramFactory(owner=user), DiagramFactory(owner=another_user)
        request = APIRequestFactory()
        request.user = user
        viewset = DiagramViewSet(request=request)
        assert viewset.get_queryset().count() == 1
        assert viewset.get_queryset().first() == instance

    def test_queryset_returns_all_diagrams_for_admin(self) -> None:
        """
        GIVEN an admin user
        WHEN get_queryset is called by admin
        THEN check that the queryset returns all diagrams.
        """
        admin, another_user = UserFactory(role=UserRoles.ADMIN), UserFactory(
            role=UserRoles.USER
        )
        instance_1, instance_2 = DiagramFactory(owner=admin), DiagramFactory(
            owner=another_user
        )
        request = APIRequestFactory()
        request.user = admin
        viewset = DiagramViewSet(request=request)
        assert viewset.get_queryset().count() == 2
        assert list(viewset.get_queryset()) == [instance_1, instance_2]

    def test_object_returns_owner_diagram_for_user(self) -> None:
        """
        GIVEN a user who owns one diagram
        WHEN get_object is called by user
        THEN check that the object returns the diagram that belongs to the user.
        """
        user, another_user = UserFactory(role=UserRoles.USER), UserFactory()
        instance, _ = DiagramFactory(owner=user), DiagramFactory(owner=another_user)
        request = APIRequestFactory()
        request.user = user
        viewset = DiagramViewSet(request=request, kwargs={"pk": instance.id})
        assert viewset.get_object() == instance

    def test_object_does_not_return_other_diagram_for_user(self) -> None:
        """
        GIVEN user without diagrams and a diagram that belongs to another user
        WHEN get_object is called by user
        THEN check that the object does not return the diagram that belongs \
        to another user.
        """
        user, another_user = UserFactory(role=UserRoles.USER), UserFactory()
        instance = DiagramFactory(owner=another_user)
        request = APIRequestFactory()
        request.user = user
        viewset = DiagramViewSet(request=request, kwargs={"pk": instance.id})
        with pytest.raises(Http404):
            viewset.get_object()

    @pytest.mark.parametrize(
        "role",
        [
            UserRoles.ADMIN,
            UserRoles.USER,
        ],
    )
    def test_object_returns_any_diagram_for_admin(self, role: str) -> None:
        """
        GIVEN an admin user
        WHEN get_object is called by admin
        THEN check that the object returns any diagram.
        """
        admin = UserFactory(role=UserRoles.ADMIN)
        owner = UserFactory(role=role)
        instance = DiagramFactory(owner=owner)
        request = APIRequestFactory()
        request.user = admin
        viewset = DiagramViewSet(request=request, kwargs={"pk": instance.id})
        assert viewset.get_object() == instance

    def test_permission_class_correct(self) -> None:
        viewset = DiagramViewSet()
        assert viewset.permission_classes == [IsAuthenticated, IsAdminOrIsOwner]


class TestCopyDiagramViewSet:
    def test_perform_create_correct(self) -> None:
        user = UserFactory(role=UserRoles.USER)
        original_diagram = DiagramFactory(owner=user)
        request = APIRequestFactory()
        request.user = user
        viewset = DiagramCopyAPIView(
            request=request, kwargs={"pk": original_diagram.id}
        )
        serializer = DiagramCopySerializer(
            original_diagram, data={"description": "copied"}, partial=True
        )
        serializer.is_valid()
        viewset.perform_create(serializer)
        assert serializer.instance != original_diagram
        assert serializer.instance.title == f"Copy of {original_diagram.title}"
        assert serializer.instance.owner == user
        assert serializer.instance.id != original_diagram.id
        assert serializer.instance.created_at != original_diagram.created_at
        assert serializer.instance.updated_at != original_diagram.updated_at

    def test_permission_class_correct(self) -> None:
        viewset = DiagramCopyAPIView()
        assert viewset.permission_classes == [IsAuthenticated, IsAdminOrIsOwner]
