from json import loads

from rest_framework import status
from rest_framework.test import APIClient

from apps.diagrams.models import Diagram
from apps.users.models import User
from tests.factories import DiagramFactory
from tests.integration.diagrams.constants import DIAGRAMS_URL


def test_update_diagram_by_authenticated_owner(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a user who owns a diagram
    WHEN he requests PUT /api/v1/diagrams/<diagram_id> with valid data
    THEN check that the diagram is updated.
    """
    diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
    fake_diagram_data = DiagramFactory.build()
    data_to_update = {
        "title": fake_diagram_data.title,
        "description": fake_diagram_data.description,
        "json": fake_diagram_data.json,
        "created_at": fake_diagram_data.created_at,
    }
    response = client.put(
        path=f"{DIAGRAMS_URL}{diagram_owned_by_user.id}/", data=data_to_update
    )
    assert response.status_code == status.HTTP_200_OK
    diagram = Diagram.objects.get(id=response.data["diagram_id"])
    assert diagram.title == response.data["title"] == data_to_update["title"]
    assert (
        diagram.description
        == response.data["description"]
        == data_to_update["description"]
    )
    assert diagram.json == response.data["json"] == loads(data_to_update["json"])
    assert diagram.updated_at > diagram_owned_by_user.updated_at
    assert (
        diagram.created_at
        == diagram_owned_by_user.created_at
        != data_to_update["created_at"]
    )


def test_update_diagram_try_to_update_another_user_diagram(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a user who does not own a diagram
    WHEN he requests PUT /api/v1/diagrams/<diagram_id> with valid data
    THEN check that the diagram is not updated.
    """
    diagram_owned_by_another_user = DiagramFactory()
    fake_diagram_data = DiagramFactory.build()
    data_to_update = {
        "title": fake_diagram_data.title,
        "description": fake_diagram_data.description,
        "json": fake_diagram_data.json,
    }
    response = client.put(
        path=f"{DIAGRAMS_URL}{diagram_owned_by_another_user.id}/", data=data_to_update
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    diagram = Diagram.objects.get(id=diagram_owned_by_another_user.id)
    assert diagram.title == diagram_owned_by_another_user.title
    assert diagram.description == diagram_owned_by_another_user.description
    assert diagram.json == diagram_owned_by_another_user.json
    assert diagram.updated_at == diagram_owned_by_another_user.updated_at


def test_update_any_diagram_by_admin(client: APIClient, logged_in_admin: User) -> None:
    """
    GIVEN an admin user and a diagram that belongs to another user
    WHEN he requests PUT /api/v1/diagrams/<diagram_id> with valid data
    THEN check that the diagram was updated.
    """
    diagram_owned_by_another_user = DiagramFactory()
    fake_diagram_data = DiagramFactory.build()
    data_to_update = {
        "title": fake_diagram_data.title,
        "description": fake_diagram_data.description,
        "json": fake_diagram_data.json,
        "owner_id": logged_in_admin.id,  # Change current owner
    }
    response = client.put(
        path=f"{DIAGRAMS_URL}{diagram_owned_by_another_user.id}/", data=data_to_update
    )
    assert response.status_code == status.HTTP_200_OK
    diagram = Diagram.objects.get(id=response.data["diagram_id"])
    assert diagram.title == response.data["title"] == data_to_update["title"]
    assert (
        diagram.description
        == response.data["description"]
        == data_to_update["description"]
    )
    assert diagram.json == response.data["json"] == loads(data_to_update["json"])
    assert diagram.owner == logged_in_admin
    assert diagram.updated_at > diagram_owned_by_another_user.updated_at
