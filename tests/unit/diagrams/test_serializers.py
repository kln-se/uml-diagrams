import pytest

from apps.diagrams.api.v1.serializers import (
    DiagramCopySerializer,
    DiagramListSerializer,
    DiagramSerializer,
    SharedDiagramListSerializer,
    SharedDiagramSaveSerializer,
)
from apps.diagrams.models import Diagram
from apps.sharings.constants import PermissionLevels
from tests.factories import DiagramFactory


@pytest.fixture
def diagram() -> Diagram:
    return DiagramFactory()


class TestDiagramSerializer:
    def test_diagram_serializer_correct_returned_data(self, diagram: Diagram) -> None:
        """
        GIVEN a random diagram object
        WHEN serializer is called
        THEN check if serialized data is coincident with the diagram's data
        and necessary fields are returned.
        """
        serializer = DiagramSerializer(diagram)
        assert serializer.data == {
            "id": str(diagram.id),
            "owner_id": diagram.owner.id,
            "owner_email": diagram.owner.email,
            "title": diagram.title,
            "json": diagram.json,
            "description": diagram.description,
            "created_at": diagram.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": diagram.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

    def test_user_serializer_update_owner_invalid_id(self, diagram: Diagram) -> None:
        """
        GIVEN a random diagram object
        WHEN serializer is called with invalid id (not uuid)
        THEN check that the serializer is not valid.
        """
        serializer = DiagramSerializer(
            diagram, data={"owner_id": "invalid_id"}, partial=True
        )
        assert not serializer.is_valid()
        assert "owner_id" in serializer.errors


class TestDiagramCopySerializer:
    def test_diagram_copy_serializer_correct_returned_data(
        self, diagram: Diagram
    ) -> None:
        """
        GIVEN a random diagram object
        WHEN serializer is called
        THEN check if serialized data is coincident with the diagram's data and
        necessary fields are returned.
        """
        serializer = DiagramCopySerializer(diagram)
        assert serializer.data == {
            "diagram_id": diagram.id,
            "title": diagram.title,
            "description": diagram.description,
            "created_at": diagram.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

    def test_diagram_copy_serializer_read_only_fields(self, diagram: Diagram) -> None:
        """
        GIVEN a random diagram object
        WHEN serializer is called with new values of read only fields to update diagram
        THEN check that the serializer is valid and the values of
        read only fields are not changed.
        """
        new_diagram_data = DiagramFactory.build()
        serializer = DiagramCopySerializer(
            diagram,
            data={
                "diagram_id": new_diagram_data.id,
                "title": new_diagram_data.title,
                "json": new_diagram_data.json,
                "created_at": new_diagram_data.created_at,
            },
            partial=True,
        )
        assert serializer.is_valid()
        instance = serializer.save()
        assert instance.id != new_diagram_data.id
        assert instance.title == diagram.title
        assert instance.json == diagram.json
        assert instance.created_at != new_diagram_data.created_at


class TestDiagramListSerializer:
    def test_diagram_list_serializer_correct_returned_data(
        self, diagram: Diagram
    ) -> None:
        """
        GIVEN a random diagram object
        WHEN serializer is called
        THEN check if serialized data is coincident with the diagram's data and
        necessary fields are returned.
        """
        serializer = DiagramListSerializer(diagram)
        assert serializer.data == {
            "diagram_id": diagram.id,
            "title": diagram.title,
            "owner_id": diagram.owner.id,
            "owner_email": diagram.owner.email,
            "created_at": diagram.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": diagram.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }


class TestSharedDiagramListSerializer:
    def test_shared_diagram_list_serializer_correct_returned_data(
        self, diagram: Diagram
    ) -> None:
        """
        GIVEN a random diagram object that has been shared to another user
        with "view-only" permission level
        WHEN serializer is called
        THEN check if serialized data is coincident with the diagram's data.
        """
        diagram.permission_level = PermissionLevels.VIEWONLY
        serializer = SharedDiagramListSerializer(diagram)
        assert serializer.data == {
            "diagram_id": diagram.id,
            "title": diagram.title,
            "owner_id": diagram.owner.id,
            "owner_email": diagram.owner.email,
            "created_at": diagram.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": diagram.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "permission_level": PermissionLevels.VIEWONLY,
        }


class TestSharedDiagramSaveSerializer:
    def test_shared_diagram_save_serializer_correct_returned_data(
        self, diagram: Diagram
    ) -> None:
        """
        GIVEN a random diagram object
        WHEN serializer is called
        THEN check if serialized data is coincident with the diagram's data
        and necessary fields are returned.
        """
        serializer = SharedDiagramSaveSerializer(diagram)
        assert serializer.data == {
            "diagram_id": diagram.id,
            "title": diagram.title,
            "description": diagram.description,
            "updated_at": diagram.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

    def test_shared_diagram_save_serializer_read_only_fields(
        self, diagram: Diagram
    ) -> None:
        """
        GIVEN a random diagram object
        WHEN serializer is called with new values of read only fields to update diagram
        THEN check that the serializer is valid and the values of
        read only fields are not changed.
        """
        new_diagram_data = DiagramFactory.build()
        serializer = SharedDiagramSaveSerializer(
            diagram,
            data={
                "title": new_diagram_data.title,
                "updated_at": new_diagram_data.updated_at,
            },
            partial=True,
        )
        assert serializer.is_valid()
        instance = serializer.save()
        assert instance.title == diagram.title
        assert instance.updated_at != new_diagram_data.updated_at
