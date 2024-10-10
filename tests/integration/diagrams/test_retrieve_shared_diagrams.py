from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import CollaboratorFactory
from tests.integration.diagrams.constants import SHARED_DIAGRAMS_URL


def test_retrieve_shared_diagrams_only_shared_diagrams_for_authenticated_collaborator(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who was invited as collaborator to 2 of 3
    diagrams
    WHEN he requests GET /api/v1/diagrams/shared-with-me/
    THEN he gets 2 diagrams shared to him and 200 OK is returned
    """
    # user was invited as collaborator to 2 different diagrams
    sharing_invitations = [
        CollaboratorFactory(shared_to=logged_in_user) for _ in range(2)
    ]
    # and was not invited to 1 diagram (3 invitations was made in total)
    _ = CollaboratorFactory()

    ordering_url_param = "?ordering=created_at"
    response = client.get(f"{SHARED_DIAGRAMS_URL}{ordering_url_param}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data["results"]
    assert len(results) == len(sharing_invitations)
    for idx, sharing_invitation in enumerate(sharing_invitations):
        diagram_data_as_dict = {
            "diagram_id": str(sharing_invitation.diagram.id),
            "title": sharing_invitation.diagram.title,
            "owner_id": str(sharing_invitation.diagram.owner.id),
            "owner_email": sharing_invitation.diagram.owner.email,
            "created_at": sharing_invitation.diagram.created_at.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "updated_at": sharing_invitation.diagram.updated_at.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "permission_level": sharing_invitation.permission_level,
        }
        assert results[idx] == diagram_data_as_dict


def test_retrieve_shared_diagrams_returns_empty_list_for_non_collaborator(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who has not invited to any diagram yet
    WHEN he requests GET /api/v1/diagrams/shared-with-me/
    THEN he gets empty list and 200 OK is returned
    """
    # some sharing invitations exist in the database
    _ = CollaboratorFactory()
    ordering_url_param = "?ordering=created_at"
    response = client.get(f"{SHARED_DIAGRAMS_URL}{ordering_url_param}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.json()["results"] == []
