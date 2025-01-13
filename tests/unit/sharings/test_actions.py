import uuid

import pytest
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.diagrams.api.v1.views import DiagramViewSet
from apps.sharings.api.v1.actions import invite_collaborator, remove_all_collaborators
from apps.sharings.constants import PermissionLevels
from apps.sharings.models import Collaborator
from apps.users.constants import UserRoles
from tests.factories import CollaboratorFactory, DiagramFactory, UserFactory


class TestActionInviteCollaborator:
    """Test @action invite_collaborator() inside DiagramViewSet."""

    def test_invite_collaborator_correct_invitation_data(self):
        """
        GIVEN correct invitation data
        WHEN invite_collaborator() action is called
        THEN 201 CREATED status code is returned
        """
        user = UserFactory(role=UserRoles.USER)
        diagram = DiagramFactory()
        invitation_data = {
            "user_email": user.email,
            "permission_level": CollaboratorFactory.build().permission_level,
        }
        request = APIRequestFactory()
        request.user = diagram.owner
        request.query_params = {}
        request.data = invitation_data
        viewset = DiagramViewSet(
            request=request,
            kwargs={"pk": diagram.id},
            format_kwarg=None,
            action=invite_collaborator.__name__,
        )
        assert viewset.get_object() == diagram
        response = viewset.invite_collaborator(request=request)
        assert response.status_code == status.HTTP_201_CREATED

    def test_invite_collaborator_diagram_does_not_exist(self):
        """
        GIVEN diagram which is shared to not registered user
        WHEN invite_collaborator() action is called
        THEN check that validation exception with "does_not_exist" error is raised
        """
        collaborator_data = CollaboratorFactory.build()
        diagram = DiagramFactory()
        invitation_data = {
            "user_email": collaborator_data.shared_to.email,
            "permission_level": collaborator_data.permission_level,
        }
        request = APIRequestFactory()
        request.user = diagram.owner
        request.query_params = {}
        request.data = invitation_data
        viewset = DiagramViewSet(
            request=request,
            kwargs={"pk": diagram.id},
            format_kwarg=None,
            action=invite_collaborator.__name__,
        )
        assert viewset.get_object() == diagram
        with pytest.raises(serializers.ValidationError) as ex:
            _ = viewset.invite_collaborator(request=request)
        assert "user_email" in ex.value.detail
        assert ex.value.detail["user_email"][0].code == "does_not_exist"


class TestActionRemoveAllCollaborators:
    """Test @action remove_all_collaborators() inside DiagramViewSet."""

    def test_remove_all_collaborators_all_collaborators_removed_successfully(self):
        """
        GIVEN a user who owns a diagram and shared it to 2 other users
        WHEN remove_all_collaborators() action is called
        THEN check that 204 NO CONTENT status code is returned and all collaborators
        were removed successfully.
        """
        diagram = DiagramFactory()
        _, _ = CollaboratorFactory(diagram=diagram), CollaboratorFactory(
            diagram=diagram
        )
        request = APIRequestFactory()
        request.user = diagram.owner
        request.query_params = {}
        viewset = DiagramViewSet(
            request=request,
            kwargs={"pk": diagram.id},
            format_kwarg=None,
            action=remove_all_collaborators.__name__,
        )
        assert viewset.get_object() == diagram
        response = viewset.remove_all_collaborators(request=request)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Collaborator.objects.count() == 0

    def test_remove_all_collaborators_diagram_does_not_exist(self):
        """
        GIVEN a user who tries to remove collaborators from not existing diagram
        WHEN remove_all_collaborators() action is called
        THEN check that there is no diagram matches the given query.
        """
        user = UserFactory(role=UserRoles.USER)
        diagram_data = DiagramFactory.build()
        request = APIRequestFactory()
        request.user = user
        request.query_params = {}
        viewset = DiagramViewSet(
            request=request,
            kwargs={"pk": diagram_data.id},
            format_kwarg=None,
            action=remove_all_collaborators.__name__,
        )
        with pytest.raises(Http404) as ex:
            _ = viewset.remove_all_collaborators(request=request)
        assert ex.value.args[0] == "No Diagram matches the given query."


class TestActionSetDiagramPublic:
    """Test @action set_diagram_public() inside DiagramViewSet."""

    def test_set_diagram_public_shared_as_public_successfully(self):
        """
        GIVEN a user who owns a diagram and shared it publicly
        WHEN set_diagram_public() action is called
        THEN check that 201 CREATED status code is returned and diagram is public.
        """
        diagram = DiagramFactory()
        request = APIRequestFactory().post("/")
        viewset = DiagramViewSet.as_view(
            actions={"post": DiagramViewSet.set_diagram_public.__name__}
        )
        force_authenticate(request, user=diagram.owner)
        response = viewset(request, pk=diagram.id)
        assert response.status_code == status.HTTP_201_CREATED
        assert Collaborator.objects.filter(diagram=diagram).first().shared_to is None

    def test_set_diagram_public_diagram_does_not_exist(self):
        """
        GIVEN a user who tries to share a not existing diagram publicly
        WHEN set_diagram_public() action is called
        THEN check that 404 NOT FOUND status code is returned.
        """
        user = UserFactory(role=UserRoles.USER)
        request = APIRequestFactory().post("/")
        viewset = DiagramViewSet.as_view(
            actions={"post": DiagramViewSet.set_diagram_public.__name__}
        )
        force_authenticate(request, user=user)
        response = viewset(request, pk=uuid.uuid4())
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_set_diagram_public_diagram_does_not_belong_to_user(self):
        """
        GIVEN a diagram which is not belongs to user, but he tries to share it publicly
        WHEN set_diagram_public() action is called
        THEN check that 404 NOT FOUND status code is returned.
        """
        user = UserFactory(role=UserRoles.USER)
        diagram_not_owned_by_user = DiagramFactory()
        request = APIRequestFactory().post("/")
        viewset = DiagramViewSet.as_view(
            actions={"post": DiagramViewSet.set_diagram_public.__name__}
        )
        force_authenticate(request, user=user)
        response = viewset(request, pk=diagram_not_owned_by_user.id)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert not Collaborator.objects.filter(
            diagram=diagram_not_owned_by_user
        ).exists()

    def test_set_diagram_public_diagram_has_been_already_public(self):
        """
        GIVEN a user who owns a public diagram and try to share it publicly again
        WHEN set_diagram_public() action is called
        THEN check that 400 BAD REQUEST status code is returned.
        """
        public_sharing = CollaboratorFactory(
            shared_to=None, permission_level=PermissionLevels.VIEWONLY
        )
        request = APIRequestFactory().post("/")
        viewset = DiagramViewSet.as_view(
            actions={"post": DiagramViewSet.set_diagram_public.__name__}
        )
        force_authenticate(request, user=public_sharing.diagram.owner)
        response = viewset(request, pk=public_sharing.diagram.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestActionSetDiagramPrivate:
    """Test @action set_diagram_private() inside DiagramViewSet."""

    def test_set_diagram_private_public_diagram_becomes_private_successfully(self):
        """
        GIVEN a user who owns a diagram which has been shared publicly
        WHEN set_diagram_private() action is called
        THEN check that 204 NO CONTENT status code was returned and the diagram
        became private.
        """
        public_sharing = CollaboratorFactory(
            shared_to=None, permission_level=PermissionLevels.VIEWONLY
        )
        request = APIRequestFactory().post("/")
        viewset = DiagramViewSet.as_view(
            actions={"post": DiagramViewSet.set_diagram_private.__name__}
        )
        force_authenticate(request, user=public_sharing.diagram.owner)
        response = viewset(request, pk=public_sharing.diagram.id)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Collaborator.objects.filter(diagram=public_sharing.diagram).exists()

    def test_set_diagram_private_diagram_does_not_exist(self):
        """
        GIVEN a user who tries to set private not existing diagram
        WHEN set_diagram_private() action is called
        THEN check that 404 NOT FOUND status code is returned.
        """
        user = UserFactory(role=UserRoles.USER)
        request = APIRequestFactory().post("/")
        viewset = DiagramViewSet.as_view(
            actions={"post": DiagramViewSet.set_diagram_private.__name__}
        )
        force_authenticate(request, user=user)
        response = viewset(request, pk=uuid.uuid4())
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_set_diagram_private_diagram_does_not_belong_to_user(self):
        """
        GIVEN a user who tries to set private the diagram which is not owned by him
        WHEN set_diagram_private() action is called
        THEN check that 404 NOT FOUND status code is returned.
        """
        user = UserFactory(role=UserRoles.USER)
        diagram_not_owned_by_user = CollaboratorFactory(
            shared_to=None, permission_level=PermissionLevels.VIEWONLY
        ).diagram
        request = APIRequestFactory().post("/")
        viewset = DiagramViewSet.as_view(
            actions={"post": DiagramViewSet.set_diagram_private.__name__}
        )
        force_authenticate(request, user=user)
        response = viewset(request, pk=diagram_not_owned_by_user.id)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Collaborator.objects.filter(diagram=diagram_not_owned_by_user).exists()

    def test_set_diagram_private_diagram_has_been_already_private(self):
        """
        GIVEN a user who owns a private diagram (has not been shared yet)
        WHEN set_diagram_private() action is called
        THEN check that 204 NO CONTENT status code is returned and the diagram
        is still private.
        """
        private_diagram = DiagramFactory()
        request = APIRequestFactory().post("/")
        viewset = DiagramViewSet.as_view(
            actions={"post": DiagramViewSet.set_diagram_private.__name__}
        )
        force_authenticate(request, user=private_diagram.owner)
        response = viewset(request, pk=private_diagram.id)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Collaborator.objects.filter(diagram=private_diagram).exists()
