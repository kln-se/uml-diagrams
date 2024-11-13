from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.diagrams.models import Diagram
from apps.sharings.models import Collaborator
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.diagrams.constants import SHARED_DIAGRAM_UNSHARE_ME_URL_NAME


class TestCopySharedDiagram:
    """
    Testing route to @action unshare_me_from_diagram()
    inside SharedWithMeDiagramViewSet.
    """

    def test_unshare_me_from_shared_diagram_by_collaborator(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who was shared a diagram to (i.e. collaborator)
        WHEN he requests
        DELETE /api/v1/diagrams/shared-with-me/{diagram_id}/unshare_me/
        THEN check that the collaborator is removed and 204 NO CONTENT is returned.
        """
        original_diagram = DiagramFactory()
        # Create a sharing invitation
        collaborator = CollaboratorFactory(
            diagram=original_diagram, shared_to=logged_in_user
        )
        url = f"{reverse(
            SHARED_DIAGRAM_UNSHARE_ME_URL_NAME,
            kwargs={'pk': original_diagram.pk}
        )}"
        # Response data check
        response = client.delete(path=url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Database data check
        assert Diagram.objects.filter(id=original_diagram.id).exists()
        assert not Collaborator.objects.filter(
            diagram=original_diagram, shared_to=collaborator.id
        ).exists()

    def test_unshare_me_from_shared_diagram_by_not_collaborator(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who was not shared a diagram to (i.e. collaborator)
        WHEN he requests
        DELETE /api/v1/diagrams/shared-with-me/{diagram_id}/unshare_me/
        THEN check that 404 NOT FOUND is returned.
        """
        original_diagram = DiagramFactory()
        # Create a sharing invitation
        some_collaborator = CollaboratorFactory(diagram=original_diagram)
        url = f"{reverse(
            SHARED_DIAGRAM_UNSHARE_ME_URL_NAME,
            kwargs={'pk': original_diagram.pk}
        )}"
        # Response data check
        response = client.delete(path=url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Database data check
        assert Diagram.objects.filter(id=original_diagram.id).exists()
        assert Collaborator.objects.filter(id=some_collaborator.id).exists()

    def test_unshare_me_from_shared_diagram_for_invalid_digram_id(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who tries to unshare himself from
        not existent diagram (invalid id).
        WHEN he requests
        DELETE /api/v1/diagrams/shared-with-me/{diagram_id}/unshare_me/
        THEN check that 404 NOT FOUND is returned.
        """
        not_existent_diagram = DiagramFactory.build()
        url = f"{reverse(
            SHARED_DIAGRAM_UNSHARE_ME_URL_NAME,
            kwargs={'pk': not_existent_diagram.pk}
        )}"
        # Response data check
        response = client.delete(path=url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
