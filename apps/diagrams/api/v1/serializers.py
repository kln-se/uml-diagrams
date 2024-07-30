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
            name="Example for admin user",
            summary="Request data example for admin user",
            description="Field **owner_id** can be set just by an admin user.",
            value={
                "owner_id": f"{uuid.uuid4()}",
                "description": "string",
            },
            request_only=True,
        ),
        OpenApiExample(
            name="Example for non-admin user",
            summary="Request data example for non-admin user",
            description="Field **owner_id** can be set just by an admin user.",
            value={
                "description": "string",
            },
            request_only=True,
        ),
    ]
)
# endregion
class DiagramCopySerializer(DiagramSerializer):
    class Meta(DiagramSerializer.Meta):
        read_only_fields = ["title", "json"]


class DiagramListSerializer(DiagramSerializer):
    """
    Used to list diagrams via GET api/v1/diagrams/
    """

    owner_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta(DiagramSerializer.Meta):
        fields = ["id", "title", "owner_id", "owner_email", "created_at", "updated_at"]
