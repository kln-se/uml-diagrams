from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import DiagramFactory
from tests.integration.diagrams.constants import DIAGRAMS_URL


def test_retrieve_diagrams_visible_to_authenticated_owner(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who owns 2 diagrams of 3
    WHEN he requests GET /api/v1/diagrams/
    THEN he gets 2 diagrams and 200 OK is returned
    """
    diagrams_owned_by_user = [DiagramFactory(owner=logged_in_user) for _ in range(2)]
    _ = DiagramFactory()  # diagram owned by another user
    response = client.get(DIAGRAMS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(diagrams_owned_by_user)
    data = response.json()
    for idx, diagram_owned_by_user in enumerate(diagrams_owned_by_user):
        diagram_data_as_dict = {
            "id": str(diagram_owned_by_user.id),
            "title": diagram_owned_by_user.title,
            "json": diagram_owned_by_user.json,
            "description": diagram_owned_by_user.description,
            "created_at": diagram_owned_by_user.created_at.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "updated_at": diagram_owned_by_user.updated_at.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
        }
        assert data[idx] == diagram_data_as_dict


def test_retrieve_all_diagrams_by_admin(
    client: APIClient, logged_in_admin: User
) -> None:
    """
    GIVEN a logged in admin user who owns 1 diagrams of 3
    WHEN he requests GET /api/v1/diagrams/
    THEN he gets all 3 diagrams and 200 OK is returned
    """
    diagrams_owned_by_some_user = [DiagramFactory() for _ in range(2)]
    diagram_owned_by_admin = DiagramFactory(owner=logged_in_admin)
    all_diagrams = [*diagrams_owned_by_some_user, diagram_owned_by_admin]
    response = client.get(DIAGRAMS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(all_diagrams)
    data = response.json()
    for idx, diagram in enumerate(all_diagrams):
        diagram_data_as_dict = {
            "id": str(diagram.id),
            "title": diagram.title,
            "json": diagram.json,
            "description": diagram.description,
            "created_at": diagram.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": diagram.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        assert data[idx] == diagram_data_as_dict
