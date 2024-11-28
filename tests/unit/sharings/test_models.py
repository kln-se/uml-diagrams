from random import choice

import pytest
from django.db import IntegrityError

from apps.sharings.constants import PermissionLevels
from tests.factories import CollaboratorFactory


def test_collaborator_model_check_constraint_prevents_instance_creation() -> None:
    """
    GIVEN a collaborator model, which describes diagram sharing details.
    WHEN trying to create its instance with incorrect conditions for public sharing:
        - permission_level being set other than "view-only";
        - shared_to=None (means diagram is shared as public).
    THEN check that constraint prevented instance from being created.
    """
    permission_level = choice([PermissionLevels.VIEWCOPY, PermissionLevels.VIEWEDIT])
    with pytest.raises(IntegrityError) as ex:
        _ = CollaboratorFactory(shared_to=None, permission_level=permission_level)
    assert ex.value.args[0] == (
        "CHECK constraint failed: "
        "shared_to_is_null_when_permission_level_is_not_view_only"
    )


def test_collaborator_model_check_constraint_allows_instance_creation() -> None:
    """
    GIVEN a collaborator model, which describes diagram sharing details.
    WHEN trying to create its instance with correct conditions for public sharing:
        - permission_level="view-only";
        - shared_to=None (means diagram is shared as public).
    THEN check that instance is created.
    """
    collaborator = CollaboratorFactory(
        shared_to=None, permission_level=PermissionLevels.VIEWONLY
    )
    assert collaborator
