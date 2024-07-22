from json import loads

import pytest
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient

from apps.diagrams.models import Diagram
from apps.users.models import User
from tests.factories import DiagramFactory
from tests.integration.diagrams.constants import DIAGRAMS_URL


@pytest.mark.parametrize(
    ("field_name", "field_value", "expected"),
    [
        ("id", Faker().pyint(), False),
        ("title", Faker().sentence(), True),
        ("description", Faker().text(), True),
        ("json", Faker().json(), True),
        ("owner", Faker().pyint(), False),
        ("updated_at", Faker().date_time(), False),
        ("created_at", Faker().date_time(), False),
    ],
)
def test_partial_update_diagram_by_authenticated_owner(
    client: APIClient,
    logged_in_user: User,
    field_name: str,
    field_value: str,
    expected: bool,
) -> None:
    """
    GIVEN a user who owns a diagram
    WHEN he requests PATCH /api/v1/diagrams/<diagram_id> with valid data
    THEN check that certain fields are updated partially.
    """
    diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
    data_to_update = {field_name: field_value}
    response = client.patch(
        path=f"{DIAGRAMS_URL}{diagram_owned_by_user.id}/", data=data_to_update
    )
    assert response.status_code == status.HTTP_200_OK
    diagram = Diagram.objects.get(id=response.data["id"])
    if field_name == "owner":
        assert (
            getattr(diagram, field_name).id == data_to_update[field_name]
        ) == expected
    elif field_name == "json":
        assert (diagram.json == loads(data_to_update[field_name])) == expected
    else:
        assert (getattr(diagram, field_name) == data_to_update[field_name]) == expected


def test_partial_update_diagram_try_to_partial_update_another_user_diagram(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a user who does not own a diagram
    WHEN he requests PATCH /api/v1/diagrams/<diagram_id> with valid data
    THEN check that the diagram field is not updated.
    """
    diagram_owned_by_another_user = DiagramFactory()
    data_to_update = {
        "title": Faker().sentence(),
    }
    response = client.patch(
        path=f"{DIAGRAMS_URL}{diagram_owned_by_another_user.id}/", data=data_to_update
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    diagram = Diagram.objects.get(id=diagram_owned_by_another_user.id)
    assert (
        diagram.title == diagram_owned_by_another_user.title != data_to_update["title"]
    )


@pytest.mark.parametrize(
    ("field_name", "field_value", "expected"),
    [
        ("id", Faker().pyint(), False),
        ("title", Faker().sentence(), True),
        ("description", Faker().text(), True),
        ("json", Faker().json(), True),
        ("owner", Faker().pyint(), True),
        ("updated_at", Faker().date_time(), False),
        ("created_at", Faker().date_time(), False),
    ],
)
def test_partial_update_any_diagram_by_admin(
    client: APIClient,
    logged_in_admin: User,
    field_name: str,
    field_value: str,
    expected: bool,
) -> None:
    """
    GIVEN an admin user and a diagram that belongs to another user
    WHEN he requests PATCH /api/v1/diagrams/<diagram_id> with valid data
    THEN check that certain fields are updated partially.
    """
    diagram_owned_by_user = DiagramFactory()
    data_to_update = {
        field_name: field_value if field_name != "owner" else logged_in_admin.id
    }
    response = client.patch(
        path=f"{DIAGRAMS_URL}{diagram_owned_by_user.id}/", data=data_to_update
    )
    assert response.status_code == status.HTTP_200_OK
    diagram = Diagram.objects.get(id=response.data["id"])
    if field_name == "owner":
        assert (
            getattr(diagram, field_name).id == data_to_update[field_name]
        ) == expected
    elif field_name == "json":
        assert (diagram.json == loads(data_to_update[field_name])) == expected
    else:
        assert (getattr(diagram, field_name) == data_to_update[field_name]) == expected
