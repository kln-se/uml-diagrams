from json import loads

from rest_framework import status
from rest_framework.test import APIClient

from apps.diagrams.models import Diagram
from apps.users.models import User
from tests.factories import DiagramFactory
from tests.integration.diagrams.constants import DIAGRAMS_URL


def test_create_diagram_by_user(client: APIClient, logged_in_user: User) -> None:
    """
    GIVEN a user who wants to create a diagram
    WHEN he requests POST /api/v1/diagrams/ with valid data
    THEN check that the diagram is created and 201 CREATED is returned.
    """
    fake_diagram_data = DiagramFactory.build()
    data_to_create = {
        "title": fake_diagram_data.title,
        "description": fake_diagram_data.description,
        "json": fake_diagram_data.json,
    }
    response = client.post(path=DIAGRAMS_URL, data=data_to_create)
    assert response.status_code == status.HTTP_201_CREATED
    diagram = Diagram.objects.get(id=response.data["id"])
    assert diagram.owner == logged_in_user
    assert diagram.title == response.data["title"] == data_to_create["title"]
    assert (
        diagram.description
        == response.data["description"]
        == data_to_create["description"]
    )
    assert diagram.json == response.data["json"] == loads(data_to_create["json"])
    assert (
        diagram.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        == response.data["created_at"]
    )
    assert (
        diagram.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        == response.data["updated_at"]
    )
