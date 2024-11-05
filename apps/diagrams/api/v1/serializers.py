import uuid

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from apps.diagrams.models import Diagram
from apps.users.models import User


# region @extend_schema_serializer
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Example for admin user",
            summary="Request data example for admin user",
            description="Field **owner_id** can be set just by an admin user.",
            value={
                "owner_id": f"{uuid.uuid4()}",
                "title": "string",
                "json": "string",
                "description": "string",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Example for non-admin user",
            summary="Request data example for non-admin user",
            description="Field **owner_id** can be set just by an admin user.",
            value={
                "title": "string",
                "json": "string",
                "description": "string",
            },
            request_only=True,
        ),
    ]
)
# endregion
class DiagramSerializer(serializers.ModelSerializer):
    json = serializers.JSONField()
    owner_id = serializers.PrimaryKeyRelatedField(
        required=False, queryset=User.objects.all()
    )
    owner_email = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Diagram
        fields = [
            "id",
            "title",
            "json",
            "description",
            "owner_id",
            "owner_email",
            "created_at",
            "updated_at",
        ]


# region @extend_schema_serializer
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="JSON body example",
            description="User can set **description** field in the request body.\n\n"
            "The **title** field is read-only. It will be automatically "
            "set to `Copy of {original_diagram_title}`.",
            value={
                "description": "string",
            },
            request_only=True,
        ),
    ]
)
# endregion
class DiagramCopySerializer(serializers.ModelSerializer):
    """
    Used to copy diagrams via POST api/v1/diagrams/{uuid}/copy/
    """

    diagram_id = serializers.ReadOnlyField(source="id")
    title = serializers.ReadOnlyField()

    class Meta:
        model = Diagram
        fields = [
            "diagram_id",
            "title",
            "description",
            "created_at",
        ]


class DiagramListSerializer(serializers.ModelSerializer):
    """
    Used to list diagrams via GET api/v1/diagrams/
    """

    diagram_id = serializers.ReadOnlyField(source="id")
    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)
    owner_email = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Diagram
        fields = [
            "diagram_id",
            "title",
            "owner_id",
            "owner_email",
            "created_at",
            "updated_at",
        ]


class SharedDiagramListSerializer(DiagramListSerializer):
    """
    Used to list diagrams via GET api/v1/diagrams/shared-with-me/.
    Diagram object is annotated with its permission level in get_queryset()
    method of SharedWithMeDiagramViewSet.
    """

    permission_level = serializers.ReadOnlyField()

    class Meta:
        model = Diagram
        fields = DiagramListSerializer.Meta.fields + ["permission_level"]
