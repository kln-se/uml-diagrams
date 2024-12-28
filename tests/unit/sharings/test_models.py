from random import choice

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.sharings.constants import PermissionLevels
from tests.factories import CollaboratorFactory, DiagramFactory


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


def test_collaborator_model_prevents_sharing_diagram_to_its_owner() -> None:
    """
    GIVEN a diagram object which is tried to be shared to its owner
    WHEN collaborator model is used to create such a sharing
    THEN check that collaborator model clean() methods raise an exception.
    """
    diagram = DiagramFactory()
    with pytest.raises(ValidationError) as ex:
        sharing = CollaboratorFactory(diagram=diagram, shared_to=diagram.owner)
        sharing.clean()
    assert ex.value.code == "self_sharing"


def test_collaborator_model_prevents_multiple_public_shares_for_the_same_diagram() -> (
    None
):
    """
    GIVEN a diagram which is tried to be shared publicly twice
    WHEN collaborator model is used to create such a sharing second time
    THEN check that collaborator model clean() methods raise an exception.
    """
    diagram = DiagramFactory()
    with pytest.raises(ValidationError) as ex:
        for _ in range(2):
            public_sharing = CollaboratorFactory(
                diagram=diagram,
                shared_to=None,
                permission_level=PermissionLevels.VIEWONLY,
            )
        public_sharing.clean()
    assert ex.value.code == "multiple_public_shares"
