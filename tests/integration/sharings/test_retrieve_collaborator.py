from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.sharings.constants import COLLABORATOR_URL


def test_retrieve_collaborator_by_authenticated_owner(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who created a sharing invitation (invited collaborator)
    WHEN he requests GET /api/v1/sharings/{collaborator_id}/
    THEN check that he gets the collaborator data and 200 OK is returned
    """
    diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
    invited_collaborator = CollaboratorFactory(diagram=diagram_owned_by_user)
    response = client.get(f"{COLLABORATOR_URL}{invited_collaborator.id}/")
    assert response.status_code == status.HTTP_200_OK
    diagram_data_as_dict = {
        "collaborator_id": str(invited_collaborator.id),
        "diagram_id": str(diagram_owned_by_user.id),
        "shared_to": invited_collaborator.shared_to.email,
        "permission_level": invited_collaborator.permission_level,
        "shared_at": invited_collaborator.shared_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    assert response.json() == diagram_data_as_dict


def test_retrieve_collaborator_try_to_access_another_user_share_invitation(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who tries to access another user's sharing invitation
    (collaborator data)
    WHEN he requests GET /api/v1/sharings/{collaborator_id}/
    THEN check that 404 NOT FOUND is returned
    """
    collaborator_invited_by_another_user = CollaboratorFactory()
    response = client.get(
        f"{COLLABORATOR_URL}{collaborator_invited_by_another_user.id}/"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_retrieve_collaborator_admin_can_retrieve_any_collaborator_data(
    client: APIClient, logged_in_admin: User
) -> None:
    """
    GIVEN a logged-in admin
    WHEN he requests GET /api/v1/sharings/{collaborator_id}/
    THEN check that he gets the collaborator data and 200 OK is returned
    """
    collaborator_invited_by_another_user = CollaboratorFactory()
    response = client.get(
        f"{COLLABORATOR_URL}{collaborator_invited_by_another_user.id}/"
    )
    assert response.status_code == status.HTTP_200_OK
    diagram_data_as_dict = {
        "collaborator_id": str(collaborator_invited_by_another_user.id),
        "diagram_id": str(collaborator_invited_by_another_user.diagram.id),
        "shared_to": collaborator_invited_by_another_user.shared_to.email,
        "permission_level": collaborator_invited_by_another_user.permission_level,
        "shared_at": collaborator_invited_by_another_user.shared_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }
    assert response.json() == diagram_data_as_dict
