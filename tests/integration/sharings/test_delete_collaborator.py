import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.sharings.models import Collaborator
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.sharings.constants import COLLABORATOR_URL


def test_delete_collaborator_by_its_inviter(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user who created a sharing invitation (invited collaborator) \
    WHEN he requests DELETE /api/v1/sharings/{collaborator_id}/
    THEN check that the collaborator is deleted and 204 NO CONTENT is returned
    """
    diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
    collaborator_invited_by_user = CollaboratorFactory(diagram=diagram_owned_by_user)
    response = client.delete(f"{COLLABORATOR_URL}{collaborator_invited_by_user.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Collaborator.DoesNotExist):
        Collaborator.objects.get(id=diagram_owned_by_user.id)


def test_delete_collaborator_collaborator_does_not_exist(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user trying to delete share invitation, created by another user
    WHEN he requests DELETE /api/v1/sharings/{collaborator_id}/
    THEN check that the collaborator is not deleted and 404 NOT FOUND is returned
    """
    collaborator = CollaboratorFactory()
    response = client.delete(f"{COLLABORATOR_URL}{collaborator.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Collaborator.objects.filter(id=collaborator.id).exists()


def test_delete_collaborator_admin_can_delete_any_collaborator(
    client: APIClient, logged_in_admin: User
) -> None:
    """
    GIVEN an admin user trying to delete share invitation, created by another user
    WHEN he requests DELETE /api/v1/sharings/{collaborator_id}/
    THEN check that the collaborator is deleted and 204 NO CONTENT is returned
    """
    collaborator_invited_by_some_user = CollaboratorFactory()
    response = client.delete(
        f"{COLLABORATOR_URL}{collaborator_invited_by_some_user.id}/"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Collaborator.DoesNotExist):
        Collaborator.objects.get(id=collaborator_invited_by_some_user.id)
