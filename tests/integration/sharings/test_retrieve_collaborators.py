from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.sharings.constants import COLLABORATOR_URL


def test_retrieve_collaborators_visible_to_authenticated_(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who invited 2 collaborators to his diagram \
    and another user invited 1 collaborator to another diagram
    WHEN he requests GET /api/v1/sharings/
    THEN he gets just his 2 collaborators and 200 OK is returned
    """
    diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
    collaborators_invited_by_user = [
        CollaboratorFactory(diagram=diagram_owned_by_user) for _ in range(2)
    ]
    _ = CollaboratorFactory()  # collaborator invited by another user
    ordering_url_param = "ordering=shared_at"
    response = client.get(f"{COLLABORATOR_URL}?{ordering_url_param}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data["results"]
    assert len(results) == len(collaborators_invited_by_user)
    for idx, collaborator in enumerate(collaborators_invited_by_user):
        collaborator_data_as_dict = {
            "collaborator_id": str(collaborator.id),
            "diagram_id": str(collaborator.diagram.id),
            "shared_to": collaborator.shared_to.email,
            "permission_level": collaborator.permission_level,
            "shared_at": collaborator.shared_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        assert results[idx] == collaborator_data_as_dict


def test_retrieve_all_collaborators_by_admin(
    client: APIClient, logged_in_admin: User
) -> None:
    """
    GIVEN a logged-in admin who invited 1 collaborator to his diagram \
    and another user invited 2 collaborators to other diagrams
    WHEN he requests GET /api/v1/sharings/
    THEN he gets all 3 sharing invitation details (collaborators data) \
    and 200 OK is returned
    """
    diagram_owned_by_admin = DiagramFactory(owner=logged_in_admin)
    collaborator_invited_by_admin = CollaboratorFactory(diagram=diagram_owned_by_admin)
    collaborators_invited_by_user = [CollaboratorFactory() for _ in range(2)]
    all_collaborators = [collaborator_invited_by_admin, *collaborators_invited_by_user]
    ordering_url_param = "ordering=shared_at"
    response = client.get(f"{COLLABORATOR_URL}?{ordering_url_param}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data["results"]
    assert len(results) == len(all_collaborators)
    for idx, collaborator in enumerate(all_collaborators):
        collaborator_data_as_dict = {
            "collaborator_id": str(collaborator.id),
            "diagram_id": str(collaborator.diagram.id),
            "shared_to": collaborator.shared_to.email,
            "permission_level": collaborator.permission_level,
            "shared_at": collaborator.shared_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }
        assert results[idx] == collaborator_data_as_dict
