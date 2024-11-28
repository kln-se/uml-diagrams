import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import CollaboratorFactory
from tests.integration.diagrams.constants import SHARED_DIAGRAMS_URL


def test_retrieve_shared_diagram_by_authenticated_collaborator(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who was shared a diagram to (i.e. collaborator)
    WHEN he requests GET /api/v1/diagrams/shared-with-me/{diagram_id}/
    THEN check that he gets the diagram and 200 OK is returned
    """
    sharing_invitation = CollaboratorFactory(shared_to=logged_in_user)
    response = client.get(f"{SHARED_DIAGRAMS_URL}{sharing_invitation.diagram.id}/")
    assert response.status_code == status.HTTP_200_OK
    diagram_data_as_dict = {
        "diagram_id": str(sharing_invitation.diagram.id),
        "title": sharing_invitation.diagram.title,
        "owner_id": str(sharing_invitation.diagram.owner.id),
        "owner_email": sharing_invitation.diagram.owner.email,
        "json": sharing_invitation.diagram.json,
        "description": sharing_invitation.diagram.description,
        "created_at": sharing_invitation.diagram.created_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "updated_at": sharing_invitation.diagram.updated_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }
    assert response.json() == diagram_data_as_dict


def test_retrieve_shared_diagram_try_to_access_diagram_shared_to_another_user(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who is not invited as collaborator but tries
    to access diagram shared to another user
    WHEN he requests GET /api/v1/diagrams/shared-with-me/{diagram_id}/
    THEN check that 404 NOT FOUND is returned
    """
    sharing_invitation = CollaboratorFactory()
    response = client.get(f"{SHARED_DIAGRAMS_URL}{sharing_invitation.diagram.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "invalid_diagram_id",
    ["invalid_diagram_id", uuid.uuid4()],
)
def test_retrieve_shared_diagram_invalid_diagram_id(
    client: APIClient, logged_in_user: User, invalid_diagram_id
) -> None:
    """
    GIVEN a logged-in user who provided an invalid diagram id in the URL
    WHEN he requests GET /api/v1/diagrams/shared-with-me/{diagram_id}/
    THEN check that 404 NOT FOUND is returned
    """
    response = client.get(f"{SHARED_DIAGRAMS_URL}{invalid_diagram_id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
