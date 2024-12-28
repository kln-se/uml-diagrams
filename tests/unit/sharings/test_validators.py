import pytest
from rest_framework import serializers

from apps.sharings.constants import PermissionLevels
from apps.sharings.validators import CollaboratorValidator
from tests.factories import CollaboratorFactory, DiagramFactory


def test_collaborator_validator_self_sharing() -> None:
    """
    GIVEN an existing_diagram which is shared to its owner
    WHEN validate_self_sharing() method is called
    THEN check that it raises validation error that self-sharing is not allowed.
    """
    existing_diagram = DiagramFactory()
    with pytest.raises(serializers.ValidationError) as ex:
        CollaboratorValidator().validate_self_sharing(
            attrs={"diagram": existing_diagram, "shared_to": existing_diagram.owner}
        )
    assert ex.value.detail[0].code == "self_sharing"


def test_collaborator_validator_non_unique_sharing() -> None:
    """
    GIVEN an existing collaborator which the same diagram is shared to again
    WHEN validate_unique_collaborator() method is called
    THEN check that it raises validation error that non-unique sharing is not allowed.
    """
    existing_collaborator = CollaboratorFactory()
    with pytest.raises(serializers.ValidationError) as ex:
        CollaboratorValidator().validate_unique_collaborator(
            attrs={
                "diagram": existing_collaborator.diagram,
                "shared_to": existing_collaborator.shared_to,
            }
        )
    assert ex.value.detail[0].code == "non_unique_sharing"


def test_collaborator_validator_multiple_public_shares() -> None:
    """
    GIVEN a diagram that has already been shared publicly
    WHEN validate_multiple_public_shares() method is called for this diagram
    THEN check that multiple public sharing validation error is raised.
    """
    existing_public_sharing = CollaboratorFactory(
        shared_to=None, permission_level=PermissionLevels.VIEWONLY
    )
    with pytest.raises(serializers.ValidationError) as ex:
        CollaboratorValidator().validate_multiple_public_shares(
            attrs={
                "diagram": existing_public_sharing.diagram,
            }
        )
    assert ex.value.detail[0].code == "multiple_public_shares"
