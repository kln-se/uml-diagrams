from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory

from apps.sharings.api.v1.pagination import CollaboratorViewSetPagination
from apps.sharings.api.v1.permissions import IsAdminOrIsSharingOwner
from apps.sharings.api.v1.views import CollaboratorViewSet
from apps.users.constants import UserRoles
from tests.factories import CollaboratorFactory, DiagramFactory, UserFactory


class TestCollaboratorViewSet:

    def test_get_queryset_returns_invited_collaborators_for_user(self) -> None:
        """
        GIVEN share invitation made by user and the one made by another user
        WHEN get_queryset is called by user
        THEN check that the queryset returns the collaborator object that \
        was created by the user.
        """
        user = UserFactory(role=UserRoles.USER)
        diagram_owned_by_user = DiagramFactory(owner=user)
        collaborator_created_by_user, _ = (
            CollaboratorFactory(diagram=diagram_owned_by_user),
            CollaboratorFactory(),
        )
        request = APIRequestFactory()
        request.user = user
        viewset = CollaboratorViewSet(request=request)
        assert viewset.get_queryset().count() == 1
        assert viewset.get_queryset().first() == collaborator_created_by_user

    def test_get_queryset_returns_all_collaborators_for_admin(self) -> None:
        """
        GIVEN share invitation made admin and the one made by another user
        WHEN get_queryset is called by user
        THEN check that the queryset returns all the collaborator objects.
        """
        admin = UserFactory(role=UserRoles.ADMIN)
        diagram_owned_by_admin = DiagramFactory(owner=admin)
        collaborator_created_by_admin, collaborator_created_by_another_user = (
            CollaboratorFactory(diagram=diagram_owned_by_admin),
            CollaboratorFactory(),
        )
        request = APIRequestFactory()
        request.user = admin
        viewset = CollaboratorViewSet(request=request)
        assert viewset.get_queryset().count() == 2
        assert list(viewset.get_queryset()) == [
            collaborator_created_by_admin,
            collaborator_created_by_another_user,
        ]

    def test_permission_class_correct(self) -> None:
        viewset = CollaboratorViewSet()
        assert viewset.permission_classes == [IsAuthenticated, IsAdminOrIsSharingOwner]

    def test_collaborator_viewset_ordering_options_correct(self) -> None:
        viewset = CollaboratorViewSet()
        assert viewset.filter_backends == [filters.OrderingFilter]
        assert viewset.ordering_fields == [
            "diagram_id",
            "shared_to",
            "permission_level",
            "shared_at",
        ]
        assert viewset.ordering == ["-shared_at"]

    def test_collaborator_viewset_pagination_class_correct(self) -> None:
        viewset = CollaboratorViewSet()
        assert viewset.pagination_class == CollaboratorViewSetPagination

    def test_collaborator_viewset_http_methods_correct(self) -> None:
        viewset = CollaboratorViewSet()
        assert viewset.http_method_names == ["get", "patch", "delete"]
