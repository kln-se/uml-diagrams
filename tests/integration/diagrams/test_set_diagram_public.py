from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.sharings.constants import PermissionLevels
from apps.sharings.models import Collaborator
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.diagrams.constants import DIAGRAM_SET_DIAGRAM_PUBLIC_URL_NAME


class TestSetDiagramPublic:
    """Test @action set_diagram_public() inside DiagramViewSet."""

    def test_set_diagram_public_shared_as_public_successfully(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who owns a diagram and share it as public
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-set-public/
        THEN check that the diagram is shared publicly and 201 CREATED is returned.
        """
        diagram = DiagramFactory(owner=logged_in_user)
        url = f"{reverse(
            DIAGRAM_SET_DIAGRAM_PUBLIC_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_201_CREATED
        collaborator = Collaborator.objects.first()
        assert collaborator.diagram == diagram
        assert collaborator.shared_to is None

    def test_set_diagram_public_diagram_does_not_exist(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user trying to share a not existed diagram as public
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-set-public/
        THEN check that 404 NOT FOUND is returned.
        """
        diagram = DiagramFactory.build()
        url = f"{reverse(
            DIAGRAM_SET_DIAGRAM_PUBLIC_URL_NAME,
            kwargs={'pk': diagram.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert not Collaborator.objects.filter(diagram=diagram).exists()

    def test_set_diagram_public_diagram_is_already_public(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who owns a diagram and have already shared it as public
        WHEN he requests POST /api/v1/diagrams/{diagram_id}/share-set-public/ again
        THEN check that 400 BAD REQUEST is returned.
        """
        diagram = DiagramFactory(owner=logged_in_user)
        public_sharing = CollaboratorFactory(
            diagram=diagram, shared_to=None, permission_level=PermissionLevels.VIEWONLY
        )
        url = f"{reverse(
            DIAGRAM_SET_DIAGRAM_PUBLIC_URL_NAME,
            kwargs={'pk': public_sharing.diagram.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["non_field_errors"][0].code == "multiple_public_shares"
