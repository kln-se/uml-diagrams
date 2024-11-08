import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.diagrams.models import Diagram
from apps.sharings.constants import PermissionLevels
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.diagrams.constants import SHARED_DIAGRAM_SAVE_URL_NAME


class TestSaveSharedDiagram:
    """
    Testing route to @action save_shared_diagram() inside SharedWithMeDiagramViewSet.
    """

    def test_save_shared_diagram_by_collaborator_with_appropriate_permission(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who was shared a diagram to (i.e. collaborator) with
        appropriate permission "view-edit"
        WHEN he requests GET /api/v1/diagrams/shared-with-me/{diagram_id}/save/
        THEN check that changes made to the diagram were applied and
        200 OK is returned.
        """
        original_diagram = DiagramFactory()
        new_diagram_data = DiagramFactory.build()
        # Create a sharing invitation
        collaborator = CollaboratorFactory(
            diagram=original_diagram,
            shared_to=logged_in_user,
            permission_level=PermissionLevels.VIEWEDIT,
        )
        data_to_set = {
            "description": new_diagram_data.description,
            "json": new_diagram_data.json,
        }
        url = f"{reverse(
            SHARED_DIAGRAM_SAVE_URL_NAME,
            kwargs={'pk': collaborator.diagram.pk}
        )}"

        # Response data check
        response = client.patch(path=url, data=data_to_set)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.keys() == {
            "diagram_id",
            "title",
            "description",
            "updated_at",
        }
        assert response.data["diagram_id"] == original_diagram.id
        assert response.data["title"] == original_diagram.title
        assert response.data["description"] == data_to_set["description"]
        assert response.data["updated_at"] > original_diagram.updated_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        # Database data check
        edited_diagram = Diagram.objects.get(id=original_diagram.id)
        assert edited_diagram.owner == original_diagram.owner
        assert edited_diagram.title == original_diagram.title
        assert edited_diagram.json == json.loads(data_to_set["json"])
        assert edited_diagram.description == data_to_set["description"]
        assert edited_diagram.updated_at > original_diagram.updated_at
        assert edited_diagram.created_at == original_diagram.created_at

    def test_save_shared_diagram_by_collaborator_with_invalid_permission(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who was shared a diagram to (i.e. collaborator) with
        not appropriate permission "view-only"
        WHEN he requests GET /api/v1/diagrams/shared-with-me/{diagram_id}/save/
        THEN check that the diagram remains unchanged and
        403 FORBIDDEN is returned.
        """
        original_diagram = DiagramFactory()
        new_diagram_data = DiagramFactory.build()
        # Create a sharing invitation
        collaborator = CollaboratorFactory(
            diagram=original_diagram,
            shared_to=logged_in_user,
            permission_level=PermissionLevels.VIEWONLY,
        )
        data_to_set = {
            "description": new_diagram_data.description,
            "json": new_diagram_data.json,
        }
        url = f"{reverse(
            SHARED_DIAGRAM_SAVE_URL_NAME,
            kwargs={'pk': collaborator.diagram.pk}
        )}"

        # Response data check
        response = client.patch(path=url, data=data_to_set)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Database data check
        edited_diagram = Diagram.objects.get(id=original_diagram.id)
        assert edited_diagram == original_diagram

    def test_save_shared_diagram_try_to_save_by_not_collaborator(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who was not shared a diagram to.
        But he tried to made changes to it.
        WHEN he requests GET /api/v1/diagrams/shared-with-me/{diagram_id}/save/
        THEN check that the diagram is remained unchanged and
        404 NOT FOUND is returned.
        """
        original_diagram = DiagramFactory()
        new_diagram_data = DiagramFactory.build()
        # Create a sharing invitation
        collaborator = CollaboratorFactory(
            diagram=original_diagram,
        )
        data_to_set = {
            "description": new_diagram_data.description,
            "json": new_diagram_data.json,
        }
        url = f"{reverse(
            SHARED_DIAGRAM_SAVE_URL_NAME,
            kwargs={'pk': collaborator.diagram.pk}
        )}"
        # Response data check
        response = client.patch(path=url, data=data_to_set)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Database data check
        edited_diagram = Diagram.objects.get(id=original_diagram.id)
        assert edited_diagram == original_diagram
