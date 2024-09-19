from rest_framework import status
from rest_framework.test import APIClient

from apps.sharings.constants import PermissionLevels
from apps.sharings.models import Collaborator
from apps.users.models import User
from tests.factories import CollaboratorFactory, DiagramFactory
from tests.integration.sharings.constants import COLLABORATOR_URL


def test_partial_update_collaborator_with_correct_permission_level_by_its_inviter(
    client: APIClient,
    logged_in_user: User,
) -> None:
    """
    GIVEN a user who created a sharing invitation (invited collaborator) \
    and updates its permission_level with the new correct value.
    WHEN he requests PATCH /api/v1/sharings/<collaborator_id> with valid id
    THEN check that the permission_level field is updated.
    """
    diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
    invited_collaborator = CollaboratorFactory(
        diagram=diagram_owned_by_user, permission_level=PermissionLevels.VIEWONLY
    )
    data_to_update = {"permission_level": PermissionLevels.VIEWCOPY}
    response = client.patch(
        path=f"{COLLABORATOR_URL}{invited_collaborator.id}/", data=data_to_update
    )
    assert response.status_code == status.HTTP_200_OK
    diagram_data_as_dict = {
        "collaborator_id": str(invited_collaborator.id),
        "diagram_id": str(diagram_owned_by_user.id),
        "shared_to": invited_collaborator.shared_to.email,
        "permission_level": data_to_update["permission_level"],
        "shared_at": invited_collaborator.shared_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    assert response.json() == diagram_data_as_dict


def test_partial_update_collaborator_with_invalid_permission_level_by_its_inviter(
    client: APIClient,
    logged_in_user: User,
) -> None:
    """
    GIVEN a user who created a sharing invitation (invited collaborator) \
    and updates its permission_level with the new but invalid value.
    WHEN he requests PATCH /api/v1/sharings/<collaborator_id> with valid id
    THEN check that the permission_level field is not updated.
    """
    diagram_owned_by_user = DiagramFactory(owner=logged_in_user)
    invited_collaborator = CollaboratorFactory(
        diagram=diagram_owned_by_user, permission_level=PermissionLevels.VIEWONLY
    )
    data_to_update = {"permission_level": "invalid_permission_level"}
    response = client.patch(
        path=f"{COLLABORATOR_URL}{invited_collaborator.id}/", data=data_to_update
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["permission_level"][0].code == "invalid_choice"
    assert (
        Collaborator.objects.first().permission_level
        == invited_collaborator.permission_level
    )


def test_partial_update_collaborator_collaborator_does_not_exist(
    client: APIClient,
    logged_in_user: User,
) -> None:
    """
    GIVEN a user who wants to update permission_level of sharing invitation, \
    created by another user.
    WHEN he requests PATCH /api/v1/sharings/<collaborator_id> with valid id
    THEN check that 404 NOT FOUND status is returned.
    """
    collaborator_invited_by_another_user = CollaboratorFactory(
        permission_level=PermissionLevels.VIEWONLY
    )
    data_to_update = {"permission_level": PermissionLevels.VIEWCOPY}
    response = client.patch(
        path=f"{COLLABORATOR_URL}{collaborator_invited_by_another_user.id}/",
        data=data_to_update,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"].code == "not_found"
    assert (
        Collaborator.objects.first().permission_level
        == collaborator_invited_by_another_user.permission_level
    )


def test_partial_update_collaborator_invalid_collaborator_id(
    client: APIClient,
    logged_in_user: User,
) -> None:
    """
    GIVEN a user who wants to update permission_level of sharing invitation, \
    but provided invalid id
    WHEN he requests PATCH /api/v1/sharings/<collaborator_id> with invalid id
    THEN check that 404 NOT FOUND status is returned.
    """
    collaborator_invited_by_another_user = CollaboratorFactory()
    data_to_update = {"permission_level": PermissionLevels.VIEWONLY}
    response = client.patch(
        path=f"{COLLABORATOR_URL}invalid_collaborator_id/", data=data_to_update
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"].code == "not_found"
    assert (
        Collaborator.objects.first().permission_level
        == collaborator_invited_by_another_user.permission_level
    )


def test_partial_update_collaborator_with_correct_permission_level_by_admin(
    client: APIClient,
    logged_in_admin: User,
) -> None:
    """
    GIVEN a sharing invitation (invited collaborator), created by some user and \
    admin trying to update its permission_level with the new correct value.
    WHEN he requests PATCH /api/v1/sharings/<collaborator_id> with valid id
    THEN check that the permission_level field is updated.
    """
    collaborator_invited_by_some_user = CollaboratorFactory(
        permission_level=PermissionLevels.VIEWONLY
    )
    data_to_update = {"permission_level": PermissionLevels.VIEWCOPY}
    response = client.patch(
        path=f"{COLLABORATOR_URL}{collaborator_invited_by_some_user.id}/",
        data=data_to_update,
    )
    assert response.status_code == status.HTTP_200_OK
    diagram_data_as_dict = {
        "collaborator_id": str(collaborator_invited_by_some_user.id),
        "diagram_id": str(collaborator_invited_by_some_user.diagram.id),
        "shared_to": collaborator_invited_by_some_user.shared_to.email,
        "permission_level": data_to_update["permission_level"],
        "shared_at": collaborator_invited_by_some_user.shared_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }
    assert response.json() == diagram_data_as_dict
