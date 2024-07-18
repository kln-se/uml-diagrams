from apps.diagrams.api.v1.serializers import DiagramCopySerializer, DiagramSerializer
from tests.factories import DiagramFactory


class TestDiagramSerializer:
    def test_diagram_serializer_correct_returned_data(self) -> None:
        """
        GIVEN a random diagram object
        WHEN serializer is called
        THEN check if serialized data is coincident with the diagram's data.
        """
        diagram = DiagramFactory()
        serializer = DiagramSerializer(diagram)
        assert serializer.data == {
            "id": diagram.id,
            "title": diagram.title,
            "json": diagram.json,
            "description": diagram.description,
            "created_at": diagram.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": diagram.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }


class TestDiagramCopySerializer:
    def test_diagram_copy_serializer_read_only_fields(self) -> None:
        """
        GIVEN a random diagram object
        WHEN serializer is called with new values of read only fields to update diagram
        THEN check that the serializer is valid and the values of
        read only fields are not changed.
        """
        diagram = DiagramFactory()
        serializer = DiagramCopySerializer(
            diagram,
            data={"title": "Changed title", "json": '{"some_new_key": "some_new_val"}'},
            partial=True,
        )
        assert serializer.is_valid()
        instance = serializer.save()
        assert instance.title == diagram.title
        assert instance.json == diagram.json
