import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.diagrams.models import Diagram
from apps.users.models import User
from tests.factories import DiagramFactory
from tests.integration.diagrams.constants import DIAGRAMS_URL


def test_delete_diagram_by_authenticated_owner(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged in user who owns a diagram
    WHEN he requests DELETE /api/v1/diagrams/{diagram_id}/
    THEN check that the diagram is deleted and 204 NO CONTENT is returned
    """
    diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
    response = client.delete(f"{DIAGRAMS_URL}{diagram_owned_by_user.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Diagram.DoesNotExist):
        Diagram.objects.get(id=diagram_owned_by_user.id)


def test_delete_diagram_try_to_delete_another_user_diagram(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged in user trying to delete another user's diagram
    WHEN he requests DELETE /api/v1/diagrams/{diagram_id}/
    THEN check that the diagram is not deleted and 404 NOT FOUND is returned
    """
    diagram_not_owned_by_user = DiagramFactory()
    response = client.delete(f"{DIAGRAMS_URL}{diagram_not_owned_by_user.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Diagram.objects.get(id=diagram_not_owned_by_user.id)


def test_delete_diagram_admin_can_retrieve_any_diagram(
    client: APIClient, logged_in_admin: User
) -> None:
    """
    GIVEN an admin user and a diagram owned by another user
    WHEN he requests DELETE /api/v1/diagrams/{diagram_id}/
    THEN check that the diagram is deleted and 204 NO CONTENT is returned
    """
    diagram = DiagramFactory()
    response = client.delete(f"{DIAGRAMS_URL}{diagram.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Diagram.DoesNotExist):
        Diagram.objects.get(id=diagram.id)
