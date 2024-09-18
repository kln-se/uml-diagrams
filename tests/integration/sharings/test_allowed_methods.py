import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.sharings.constants import COLLABORATOR_URL


class TestCollaboratorDetailAllowedHttpMethods:
    """
    CollaboratorViewset allowed HTTP methods.
    """

    @pytest.mark.parametrize(
        ("method", "status_code"),
        [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("patch", status.HTTP_200_OK),
            ("delete", status.HTTP_204_NO_CONTENT),
        ],
    )
    def test_collaborator_detail_allowed_http_methods(
        self, client: APIClient, logged_in_user: User, method: str, status_code: int
    ) -> None:
        """
        GIVEN a logged-in user
        WHEN GET, PATCH, DELETE methods for /api/v1/sharings/{uuid} are requested
        THEN check that 2XX success code is returned.
        """
        diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
        collaborator = CollaboratorFactory(diagram=diagram_owned_by_user)
        response = getattr(client, method)(
            path=f"{COLLABORATOR_URL}{collaborator.id}/",
        )
        assert response.status_code == status_code
