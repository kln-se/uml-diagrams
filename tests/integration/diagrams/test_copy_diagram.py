from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient

from apps.diagrams.models import Diagram
from apps.users.models import User
from tests.factories import DiagramFactory
from tests.integration.diagrams.constants import DIAGRAM_COPY_URL_NAME


class TestCopyDiagram:
    """Testing route to @action copy_diagram() inside DiagramViewSet."""

    def test_copy_diagram_by_authenticated_owner(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a logged-in user who owns a diagram
        WHEN he requests POST /api/v1/diagrams/{pk}/copy/
        THEN check that diagram is copied and 201 OK is returned
        """
        diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
        data_to_set = {
            "description": Faker().text(),
        }
        url = (
            f"{reverse(DIAGRAM_COPY_URL_NAME, kwargs={'pk': diagram_owned_by_user.pk})}"
        )
        response = client.post(path=url, data=data_to_set)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["diagram_id"] != diagram_owned_by_user.id
        assert response.data["title"] == f"Copy of {diagram_owned_by_user.title}"
        assert (
            response.data["description"]
            == data_to_set["description"]
            != diagram_owned_by_user.description
        )
        assert response.data["created_at"] > diagram_owned_by_user.created_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        copied_diagram = Diagram.objects.get(id=response.data["diagram_id"])
        assert copied_diagram.owner == logged_in_user
        assert copied_diagram.json == diagram_owned_by_user.json

    def test_copy_diagram_user_tries_to_copy_another_user_diagram(
        self, client: APIClient, logged_in_user: User
    ) -> None:
        """
        GIVEN a diagram that belongs to another user
        WHEN he requests POST /api/v1/diagrams/{pk}/copy/
        THEN check that 404 NOT FOUND is returned
        """
        diagram_owned_by_another_user = DiagramFactory()
        url = f"{reverse(
            DIAGRAM_COPY_URL_NAME,
            kwargs={'pk': diagram_owned_by_another_user.pk}
        )}"
        response = client.post(path=url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert not Diagram.objects.filter(owner=logged_in_user).exists()

    def test_copy_any_diagram_by_admin(
        self, client: APIClient, logged_in_admin: User
    ) -> None:
        """
        GIVEN an admin user and a diagram that belongs to another user
        WHEN he requests POST /api/v1/diagrams/{pk}/copy/
        THEN check that diagram is copied and 201 OK is returned
        """
        diagram_owned_by_another_user = DiagramFactory()
        data_to_set = {
            "description": Faker().text(),
        }
        url = f"{reverse(
            DIAGRAM_COPY_URL_NAME,
            kwargs={'pk': diagram_owned_by_another_user.pk}
        )}"
        response = client.post(path=url, data=data_to_set)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["diagram_id"] != diagram_owned_by_another_user.id
        assert (
            response.data["title"] == f"Copy of {diagram_owned_by_another_user.title}"
        )
        assert (
            response.data["description"]
            == data_to_set["description"]
            != diagram_owned_by_another_user.description
        )
        assert response.data[
            "created_at"
        ] > diagram_owned_by_another_user.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        copied_diagram = Diagram.objects.get(id=response.data["diagram_id"])
        assert copied_diagram.owner == logged_in_admin
        assert copied_diagram.json == diagram_owned_by_another_user.json
