import pytest
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.test import APIRequestFactory

from apps.diagrams.api.v1.views import DiagramViewSet
from apps.sharings.api.v1.actions import invite_collaborator, remove_all_collaborators
from apps.sharings.models import Collaborator
from apps.users.constants import UserRoles
from tests.factories import CollaboratorFactory, DiagramFactory, UserFactory


class TestActionInviteCollaborator:

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
