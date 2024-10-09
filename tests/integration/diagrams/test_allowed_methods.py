import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import CollaboratorFactory
from tests.integration.diagrams.constants import SHARED_DIAGRAMS_URL


class TestSharedWithMeDiagramAllowedHttpMethods:
    """
    SharedWithMeDiagramViewset allowed HTTP methods.
    """

    @pytest.mark.parametrize(
        ("method", "status_code"),
        [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("delete", status.HTTP_405_METHOD_NOT_ALLOWED),
        ],
    )
    def test_shared_with_me_diagram_list_allowed_http_methods(
        self, client: APIClient, logged_in_user: User, method: str, status_code: int
    ) -> None:
        """
        GIVEN a logged-in user
        WHEN POST, PUT, PATCH, DELETE methods
        for /api/v1/diagrams/shared-with-me/ are requested
        THEN check that 405 METHOD NOT ALLOWED code is returned.
        """
        response = getattr(client, method)(
            path=SHARED_DIAGRAMS_URL,
        )
        assert response.status_code == status_code

    @pytest.mark.parametrize(
        ("method", "status_code"),
        [
            ("get", status.HTTP_200_OK),
            ("post", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("patch", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("delete", status.HTTP_405_METHOD_NOT_ALLOWED),
        ],
    )
    def test_shared_with_me_diagram_detail_allowed_http_methods(
        self, client: APIClient, logged_in_user: User, method: str, status_code: int
    ) -> None:
        """
        GIVEN a logged-in user
        WHEN PUT, PATCH, DELETE methods
        for /api/v1/diagrams/shared-with-me/ are requested
        THEN check that 405 METHOD NOT ALLOWED code is returned.
        """
        collaborator = CollaboratorFactory(shared_to=logged_in_user)
        response = getattr(client, method)(
            path=f"{SHARED_DIAGRAMS_URL}{collaborator.diagram.id}/",
        )
        assert response.status_code == status_code
