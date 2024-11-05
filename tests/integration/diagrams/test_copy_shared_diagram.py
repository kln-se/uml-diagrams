from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.diagrams.models import Diagram
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.diagrams.constants import SHARED_DIAGRAM_COPY_URL_NAME


class TestCopySharedDiagram:
    """
    Testing route to @action copy_shared_diagram() inside SharedWithMeDiagramViewSet.
    """

    def test_copy_shared_diagram_by_collaborator_with_appropriate_permission(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who was shared a diagram to (i.e. collaborator) with
        appropriate permission "view-copy"
        WHEN he requests GET /api/v1/diagrams/shared-with-me/{diagram_id}/copy/
        THEN check that the diagram is copied and 200 OK is returned
        """
        original_diagram = DiagramFactory()
        # Create a sharing invitation
        collaborator = CollaboratorFactory(
            diagram=original_diagram,
            shared_to=logged_in_user,
            permission_level="view-copy",
        )
        data_to_set = {
            "description": "Copied.",
        }
        url = f"{reverse(
            SHARED_DIAGRAM_COPY_URL_NAME,
            kwargs={'pk': collaborator.diagram.pk}
        )}"
        response = client.post(path=url, data=data_to_set)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["diagram_id"] != original_diagram.id
        assert response.data["title"] == f"Copy of {original_diagram.title}"
        assert (
            response.data["description"]
            == data_to_set["description"]
            != original_diagram.description
        )
        assert response.data["created_at"] > original_diagram.created_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        copied_diagram = Diagram.objects.get(id=response.data["diagram_id"])
        assert copied_diagram.owner == collaborator.shared_to
        assert copied_diagram.json == original_diagram.json
        assert copied_diagram.title == f"Copy of {original_diagram.title}"

    def test_copy_shared_diagram_by_collaborator_with_invalid_permission(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who was shared a diagram to (i.e. collaborator) with
        not appropriate permission "view-only"
        WHEN he requests GET /api/v1/diagrams/shared-with-me/{diagram_id}/copy/
        THEN check that the diagram is not copied and 403 FORBIDDEN is returned
        """
        original_diagram = DiagramFactory()
        # Create a sharing invitation
        collaborator = CollaboratorFactory(
            diagram=original_diagram,
            shared_to=logged_in_user,
            permission_level="view-only",
        )
        data_to_set = {
            "description": "Copied.",
        }
        url = f"{reverse(
            SHARED_DIAGRAM_COPY_URL_NAME,
            kwargs={'pk': collaborator.diagram.pk}
        )}"
        response = client.post(path=url, data=data_to_set)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Diagram.objects.count() == 1
        assert not Diagram.objects.filter(owner=logged_in_user).exists()

    def test_copy_shared_diagram_try_to_copy_by_not_collaborator(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who was not shared a diagram to. But he tried to copy it.
        WHEN he requests GET /api/v1/diagrams/shared-with-me/{diagram_id}/copy/
        THEN check that the diagram is not copied and 404 NOT FOUND is returned
        """
        original_diagram = DiagramFactory()
        # Create a sharing invitation
        some_collaborator = CollaboratorFactory(
            diagram=original_diagram, permission_level="view-copy"
        )
        data_to_set = {
            "description": "I try to copy it anyway!",
        }
        url = f"{reverse(
            SHARED_DIAGRAM_COPY_URL_NAME,
            kwargs={'pk': some_collaborator.diagram.pk}
        )}"
        response = client.post(path=url, data=data_to_set)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Diagram.objects.count() == 1
        assert not Diagram.objects.filter(owner=logged_in_user).exists()
