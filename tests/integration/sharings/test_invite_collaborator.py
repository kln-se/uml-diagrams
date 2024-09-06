from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.sharings.models import Collaborator
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory, UserFactory
from tests.integration.sharings.constants import DIAGRAM_SHARE_INVITE_USER_URL_NAME


class TestInviteCollaboratorToDiagram:
    """Testing @action invite_collaborator() inside DiagramViewSet."""

    def test_invite_collaborator_to_diagram_correct_invitation_data(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who owns a diagram and share it to another user
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-invite-user/
        THEN check that the diagram is shared and 201 CREATED is returned
        """
        user = UserFactory()
        diagram = DiagramFactory(owner=logged_in_user)
        invitation_data = {
            "user_email": user.email,
            "permission_level": CollaboratorFactory.build().permission_level,
        }
        url = f"{reverse(
            DIAGRAM_SHARE_INVITE_USER_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url, data=invitation_data)
        assert response.status_code == status.HTTP_201_CREATED
        collaborator = Collaborator.objects.first()
        assert collaborator.diagram == diagram
        assert collaborator.diagram_id == response.data["diagram_id"]
        assert collaborator.shared_to == user
        assert collaborator.shared_to.email == response.data["shared_to"]
        assert (
            invitation_data["permission_level"]
            == collaborator.permission_level
            == response.data["permission_level"]
        )

    def test_invite_collaborator_to_diagram_diagram_does_not_exist(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user trying to share a not existed diagram to another user
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-invite-user/
        THEN check that 404 NOT FOUND is returned
        """
        user = UserFactory()
        diagram = DiagramFactory.build()
        invitation_data = {
            "user_email": user.email,
            "permission_level": CollaboratorFactory.build().permission_level,
        }
        url = f"{reverse(
            DIAGRAM_SHARE_INVITE_USER_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url, data=invitation_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"].code == "not_found"
        assert not Collaborator.objects.first()

    def test_invite_collaborator_to_diagram_user_does_not_exist(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who owns a diagram and trying to share it to a \
        not exist user
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-invite-user/
        THEN check that 400 BAD REQUEST is returned
        """
        collaborator_data = CollaboratorFactory.build()
        diagram = DiagramFactory(owner=logged_in_user)
        invitation_data = {
            "user_email": collaborator_data.shared_to.email,
            "permission_level": collaborator_data.permission_level,
        }
        url = f"{reverse(
            DIAGRAM_SHARE_INVITE_USER_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url, data=invitation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["user_email"][0].code == "does_not_exist"
        assert not Collaborator.objects.first()

    def test_invite_collaborator_to_diagram_user_permission_level_is_invalid(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user trying to share a diagram to another user with invalid \
        permission level
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-invite-user/
        THEN check that 400 BAD REQUEST is returned
        """
        user = UserFactory()
        diagram = DiagramFactory(owner=logged_in_user)
        invitation_data = {
            "user_email": user.email,
            "permission_level": "invalid_permission_level",
        }
        url = f"{reverse(
            DIAGRAM_SHARE_INVITE_USER_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url, data=invitation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["permission_level"][0].code == "invalid_choice"
        assert not Collaborator.objects.first()

    def test_invite_collaborator_to_diagram_self_sharing(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user trying to share his diagram to himself
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-invite-user/
        THEN check that 400 BAD REQUEST is returned
        """
        diagram = DiagramFactory(owner=logged_in_user)
        invitation_data = {
            "user_email": logged_in_user.email,
            "permission_level": CollaboratorFactory.build().permission_level,
        }
        url = f"{reverse(
            DIAGRAM_SHARE_INVITE_USER_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url, data=invitation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"][0].code == "self_sharing"
        assert not Collaborator.objects.first()

    def test_invite_collaborator_to_diagram_non_unique_sharing(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user trying to share his diagram to the same user twice
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-invite-user/
        THEN check that 400 BAD REQUEST is returned
        """
        user = UserFactory()
        diagram = DiagramFactory(owner=logged_in_user)
        collaborator = CollaboratorFactory(diagram=diagram, shared_to=user)
        invitation_data = {
            "user_email": collaborator.shared_to.email,
            "permission_level": collaborator.permission_level,
        }
        url = f"{reverse(
            DIAGRAM_SHARE_INVITE_USER_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url, data=invitation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"][0].code == "non_unique_sharing"
        assert len(Collaborator.objects.all()) == 1

    def test_invite_collaborator_to_diagram_admin_invite_user_to_alien_diagram(
        self, client: APIClient, logged_in_admin: User
    ) -> None:
        """
        GIVEN a logged-in admin who trying to share an alien diagram to another user
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-invite-user/
        THEN check that the diagram is shared and 201 CREATED is returned
        """
        user = UserFactory()
        diagram = DiagramFactory()
        invitation_data = {
            "user_email": user.email,
            "permission_level": CollaboratorFactory.build().permission_level,
        }
        url = f"{reverse(
            DIAGRAM_SHARE_INVITE_USER_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url, data=invitation_data)
        assert response.status_code == status.HTTP_201_CREATED
        collaborator = Collaborator.objects.first()
        assert collaborator.diagram == diagram
        assert collaborator.shared_to == user
