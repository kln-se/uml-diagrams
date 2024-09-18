import pytest

from apps.sharings.api.v1.serializers import (
    CollaboratorSerializer,
    InviteCollaboratorSerializer,
)
from apps.sharings.models import Collaborator
from tests.factories import CollaboratorFactory, DiagramFactory, UserFactory


@pytest.fixture
def collaborator() -> Collaborator:
    return CollaboratorFactory()


class TestInviteCollaboratorSerializer:

    def test_invite_collaborator_serializer_returned_data(
        self, collaborator: Collaborator
    ) -> None:
        """
        GIVEN a random collaborator object
        WHEN serializer is called
        THEN check if serialized data is coincident with the collaborator's data.
        """
        serializer = InviteCollaboratorSerializer(instance=collaborator)
        assert serializer.data == {
            "collaborator_id": collaborator.id,
            "diagram_id": collaborator.diagram.id,
            "shared_to": collaborator.shared_to.email,
            "permission_level": collaborator.permission_level,
        }

    def test_invite_collaborator_serializer_input_data_correct(self) -> None:
        """
        GIVEN an existed diagram which is shared to an existed user
        WHEN serializer is called
        THEN check that data serialized to Collaborator object correctly.
        """
        existing_diagram = DiagramFactory()
        existing_user = UserFactory()
        invitation_data = {
            "user_email": existing_user.email,
            "permission_level": CollaboratorFactory.build().permission_level,
        }
        # diagram_id is taken from url,
        # so it provided to serializer not in input but in context
        serializer = InviteCollaboratorSerializer(
            data=invitation_data, context={"diagram": existing_diagram}
        )
        serializer.is_valid(raise_exception=True)
        # serializer does not validate diagram_id itself, but use it in
        # validate() method to check self-sharing and non-unique sharing,
        # so we provide it inside validated_data
        serializer.validated_data["diagram"] = existing_diagram
        instance: Collaborator = serializer.create(
            validated_data=serializer.validated_data
        )
        assert instance.shared_to.email == invitation_data["user_email"]
        assert instance.permission_level == invitation_data["permission_level"]

    def test_invite_collaborator_serializer_input_data_user_does_not_exist(
        self,
    ) -> None:
        """
        GIVEN invitation data with non-existent user email
        WHEN serializer is called
        THEN check that serializer raises error that user does not exist.
        """
        collaborator_data = CollaboratorFactory.build()
        invitation_data = {
            "user_email": collaborator_data.shared_to.email,
            "permission_level": collaborator_data.permission_level,
        }
        serializer = InviteCollaboratorSerializer(data=invitation_data)
        assert not serializer.is_valid()
        assert "user_email" in serializer.errors
        assert serializer.errors["user_email"][0].code == "does_not_exist"

    def test_invite_collaborator_serializer_input_data_permission_level_is_invalid(
        self, collaborator: Collaborator
    ) -> None:
        """
        GIVEN invitation data with incorrect permission level provided
        WHEN serializer is called
        THEN check that serializer raises error that permission level is invalid.
        """
        collaborator_data = CollaboratorFactory.build()
        invitation_data = {
            "user_email": collaborator_data.shared_to.email,
            "permission_level": "invalid_permission_level",
        }
        serializer = InviteCollaboratorSerializer(data=invitation_data)
        assert not serializer.is_valid()
        assert "permission_level" in serializer.errors
        assert serializer.errors["permission_level"][0].code == "invalid_choice"

    def test_invite_collaborator_serializer_validate_self_sharing(self) -> None:
        """
        GIVEN an invitation data where provided user_email is the same as diagram owner
        WHEN validate() method inside serializer is called
        THEN check that serializer raises error that self-sharing is not allowed.
        """
        existing_diagram = DiagramFactory()
        invitation_data = {
            "user_email": existing_diagram.owner.email,
            "permission_level": CollaboratorFactory.build().permission_level,
        }
        serializer = InviteCollaboratorSerializer(
            data=invitation_data, context={"diagram": existing_diagram}
        )
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
        assert serializer.errors["non_field_errors"][0].code == "self_sharing"

    def test_invite_collaborator_serializer_validate_non_unique_sharing(
        self, collaborator: Collaborator
    ) -> None:
        """
        GIVEN a data with user_email which that diagram_id has already been shared to
        WHEN validate() method inside serializer is called
        THEN check that serializer raises error that non-unique sharing is not allowed.
        """
        invitation_data = {
            "user_email": collaborator.shared_to.email,
            "permission_level": collaborator.permission_level,
        }
        serializer = InviteCollaboratorSerializer(
            data=invitation_data, context={"diagram": collaborator.diagram}
        )
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
        assert serializer.errors["non_field_errors"][0].code == "non_unique_sharing"


class TestCollaboratorSerializer:
    def test_collaborator_serializer_returned_data(
        self, collaborator: Collaborator
    ) -> None:
        """
        GIVEN a random collaborator object
        WHEN serializer is called
        THEN check if serialized data is coincident with the collaborator's data.
        """
        serializer = CollaboratorSerializer(instance=collaborator)
        assert serializer.data == {
            "collaborator_id": collaborator.id,
            "diagram_id": collaborator.diagram.id,
            "shared_to": collaborator.shared_to.email,
            "permission_level": collaborator.permission_level,
            "shared_at": collaborator.shared_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

    def test_collaborator_serializer_input_data_correct(self) -> None:
        """
        GIVEN a new correct permission level for collaborator to update
        WHEN serializer is called
        THEN check that serializer is valid.
        """
        data_to_update = {
            "permission_level": CollaboratorFactory.build().permission_level,
        }
        serializer = CollaboratorSerializer(data=data_to_update)
        assert serializer.is_valid()
        assert "permission_level" not in serializer.errors

    def test_collaborator_serializer_input_data_is_invalid(self) -> None:
        """
        GIVEN a new invalid permission level for collaborator to update
        WHEN serializer is called
        THEN check that serializer is not valid.
        """
        data_to_update = {
            "permission_level": "invalid_permission_level",
        }
        serializer = CollaboratorSerializer(data=data_to_update)
        assert not serializer.is_valid()
        assert "permission_level" in serializer.errors
