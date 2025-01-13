import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.sharings.constants import PermissionLevels
from apps.sharings.models import Collaborator
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.diagrams.constants import DIAGRAM_SET_DIAGRAM_PRIVATE_URL_NAME


class TestSetDiagramPrivate:
    """Test @action set_diagram_private() inside DiagramViewSet."""

    def test_set_diagram_private_public_diagram_becomes_private_successfully(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who owns a diagram and share it as public
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-set-private/
        THEN check that the diagram is shared publicly and 201 CREATED is returned.
        """
        diagram = DiagramFactory(owner=logged_in_user)
        _ = CollaboratorFactory(
            diagram=diagram, shared_to=None, permission_level=PermissionLevels.VIEWONLY
        )
        url = f"{reverse(
            DIAGRAM_SET_DIAGRAM_PRIVATE_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Collaborator.objects.filter(diagram=diagram).exists()

    def test_set_diagram_private_diagram_does_not_exist(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user trying to share a not existed diagram as public
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-set-private/
        THEN check that 404 NOT FOUND is returned.
        """
        url = f"{reverse(
            DIAGRAM_SET_DIAGRAM_PRIVATE_URL_NAME,
            kwargs={'pk': uuid.uuid4()}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_set_diagram_private_diagram_does_not_belong_to_user(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who tries to set private the diagram
        which is not owned by him
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-set-private/
        THEN check that 404 NOT FOUND is returned.
        """
        diagram_not_owned_by_user = CollaboratorFactory(
            shared_to=None, permission_level=PermissionLevels.VIEWONLY
        ).diagram
        url = f"{reverse(
            DIAGRAM_SET_DIAGRAM_PRIVATE_URL_NAME,
            kwargs={'pk': diagram_not_owned_by_user.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Collaborator.objects.filter(diagram=diagram_not_owned_by_user).exists()

    def test_set_diagram_private_diagram_has_been_already_private(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who owns a private diagram (has not been shared yet)
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-set-private/ again
        THEN check that 204 NO CONTENT is returned.
        """
        private_diagram = DiagramFactory(owner=logged_in_user)
        url = f"{reverse(
            DIAGRAM_SET_DIAGRAM_PRIVATE_URL_NAME,
            kwargs={'pk': private_diagram.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Collaborator.objects.filter(diagram=private_diagram).exists()
