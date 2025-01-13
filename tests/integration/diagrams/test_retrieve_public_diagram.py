import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.sharings.constants import PermissionLevels
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.diagrams.constants import PUBLIC_DIAGRAMS_URL_NAME


def test_retrieve_publicly_shared_diagram_by_anonymous_user(client: APIClient) -> None:
    """
    GIVEN a publicly shared diagram and an anonymous user
    WHEN he requests GET /api/v1/diagrams/public/{diagram_id}/
    THEN check that he gets the diagram and 200 OK is returned
    """
    public_sharing = CollaboratorFactory(
        shared_to=None, permission_level=PermissionLevels.VIEWONLY
    )
    url = f"{reverse(
        PUBLIC_DIAGRAMS_URL_NAME,
        kwargs={'pk': public_sharing.diagram.pk}
    )}"
    response = client.get(path=url)
    assert response.status_code == status.HTTP_200_OK
    diagram_data_as_dict = {
        "diagram_id": str(public_sharing.diagram.id),
        "title": public_sharing.diagram.title,
        "owner_id": str(public_sharing.diagram.owner.id),
        "owner_email": public_sharing.diagram.owner.email,
        "json": public_sharing.diagram.json,
        "description": public_sharing.diagram.description,
        "created_at": public_sharing.diagram.created_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "updated_at": public_sharing.diagram.updated_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }
    assert response.json() == diagram_data_as_dict


@pytest.mark.parametrize(
    "invalid_diagram_id",
    ["some-invalid-diagram-id", uuid.uuid4()],
)
def test_retrieve_publicly_shared_diagram_invalid_diagram_id(
    client: APIClient, invalid_diagram_id
) -> None:
    """
    GIVEN an anonymous user, who provided an invalid diagram id in the URL
    WHEN he requests GET /api/v1/diagrams/public/{diagram_id}/
    THEN check that 404 NOT FOUND is returned
    """
    url = f"{reverse(
        PUBLIC_DIAGRAMS_URL_NAME,
        kwargs={'pk': invalid_diagram_id}
    )}"
    response = client.get(path=url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_try_to_retrieve_not_shared_diagram(client: APIClient) -> None:
    """
    GIVEN an anonymous user trying to retrieve a diagram which is not shared to anyone
    WHEN he requests GET /api/v1/diagrams/public/{diagram_id}/
    THEN check that he gets 404 NOT FOUND
    """
    not_shared_diagram = DiagramFactory()
    url = f"{reverse(
        PUBLIC_DIAGRAMS_URL_NAME,
        kwargs={'pk': not_shared_diagram.id}
    )}"
    response = client.get(path=url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_try_to_retrieve_diagram_shared_personally_not_public(
    client: APIClient,
) -> None:
    """
    GIVEN an anonymous user trying to retrieve a diagram which is not shared as public
    but shared to someone
    WHEN he requests GET /api/v1/diagrams/public/{diagram_id}/
    THEN check that he gets 404 NOT FOUND
    """
    shared_diagram = CollaboratorFactory().diagram
    url = f"{reverse(
        PUBLIC_DIAGRAMS_URL_NAME,
        kwargs={'pk': shared_diagram.id}
    )}"
    response = client.get(path=url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
