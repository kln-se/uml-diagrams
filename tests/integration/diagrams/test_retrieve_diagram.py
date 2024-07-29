from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import DiagramFactory
from tests.integration.diagrams.constants import DIAGRAMS_URL


def test_retrieve_diagram_by_authenticated_owner(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who owns a diagram
    WHEN he requests GET /api/v1/diagrams/{diagram_id}/
    THEN check that he gets the diagram and 200 OK is returned
    """
    diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
    response = client.get(f"{DIAGRAMS_URL}{diagram_owned_by_user.id}/")
    assert response.status_code == status.HTTP_200_OK
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
    assert response.json() == diagram_data_as_dict


def test_retrieve_diagram_try_to_access_another_user_diagram(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who tries to access another user's diagram
    WHEN he requests GET /api/v1/diagrams/{diagram_id}/
    THEN check that 404 NOT FOUND is returned
    """
    diagram_owned_by_another_user = DiagramFactory()
    response = client.get(f"{DIAGRAMS_URL}{diagram_owned_by_another_user.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_retrieve_diagram_admin_can_retrieve_any_diagram(
    client: APIClient, logged_in_admin: User
) -> None:
    """
    GIVEN a logged-in admin
    WHEN he requests GET /api/v1/diagrams/{diagram_id}/
    THEN check that he gets the diagram and 200 OK is returned
    """
    diagram_owned_by_another_user = DiagramFactory()
    response = client.get(f"{DIAGRAMS_URL}{diagram_owned_by_another_user.id}/")
    assert response.status_code == status.HTTP_200_OK
    diagram_data_as_dict = {
        "id": str(diagram_owned_by_another_user.id),
        "title": diagram_owned_by_another_user.title,
        "json": diagram_owned_by_another_user.json,
        "description": diagram_owned_by_another_user.description,
        "created_at": diagram_owned_by_another_user.created_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "updated_at": diagram_owned_by_another_user.updated_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }
    assert response.json() == diagram_data_as_dict
