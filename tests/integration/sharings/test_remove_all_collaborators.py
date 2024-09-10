from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.sharings.models import Collaborator
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.sharings.constants import DIAGRAM_SHARE_UNSHARE_ALL_URL_NAME


class TestRemoveAllCollaboratorsFromDiagram:
    """Testing @action remove_all_collaborators() inside DiagramViewSet."""

    def test_remove_all_collaborators_all_collaborators_removed_successfully(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a user who owns a diagram and shared it to 2 other users
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-unshare-all/
        THEN check that 204 NO CONTENT status code is returned and all collaborators
        were removed successfully.
        """
        diagram = DiagramFactory(owner=logged_in_user)
        _, _ = CollaboratorFactory(diagram=diagram), CollaboratorFactory(
            diagram=diagram
        )
        url = f"{reverse(
            DIAGRAM_SHARE_UNSHARE_ALL_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Collaborator.objects.count() == 0

    def test_remove_all_collaborators_diagram_has_no_collaborators_yet(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a user who owns a diagram but has not shared it to any other user yet
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-unshare-all/
        THEN check that 204 NO CONTENT status code is returned with no errors.
        """
        diagram = DiagramFactory(owner=logged_in_user)
        url = f"{reverse(
            DIAGRAM_SHARE_UNSHARE_ALL_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Collaborator.objects.count() == 0

    def test_remove_all_collaborators_diagram_does_not_exist(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a user who tries to remove collaborators from not existing diagram
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-unshare-all/
        THEN check that 404 NOT FOUND is returned.
        """
        diagram_data = DiagramFactory.build()
        url = f"{reverse(
            DIAGRAM_SHARE_UNSHARE_ALL_URL_NAME,
            kwargs={'pk': diagram_data.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"].code == "not_found"
        assert Collaborator.objects.count() == 0

    def test_remove_all_collaborators_admin_remove_collaborators_from_alien_diagram(
        self, client: APIClient, logged_in_admin: User
    ) -> None:
        """
        GIVEN a diagram that does not belong to admin. It was shared to 2 other users.
        Admin tries to remove collaborators from this diagram.
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-unshare-all/
        THEN check that 204 NO CONTENT status code is returned and all collaborators
        were removed successfully.
        """
        another_user_diagram = DiagramFactory()
        _, _ = CollaboratorFactory(diagram=another_user_diagram), CollaboratorFactory(
            diagram=another_user_diagram
        )
        url = f"{reverse(
            DIAGRAM_SHARE_UNSHARE_ALL_URL_NAME,
            kwargs={'pk': another_user_diagram.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Collaborator.objects.count() == 0
