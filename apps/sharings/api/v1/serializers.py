import uuid
from datetime import datetime, timezone

from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from apps.sharings.constants import PermissionLevels
from apps.sharings.models import Collaborator
from apps.sharings.validators import CollaboratorValidator
from apps.users.models import User


class InviteCollaboratorSerializer(serializers.ModelSerializer):
    user_email = serializers.SlugRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        slug_field="email",
        source="shared_to",
        allow_null=False,
    )
    permission_level = serializers.ChoiceField(choices=PermissionLevels.CHOICES)
    diagram_id = serializers.ReadOnlyField(source="diagram.id")
    shared_to = serializers.ReadOnlyField(source="shared_to.email")
    collaborator_id = serializers.ReadOnlyField(source="id")

    class Meta:
        model = Collaborator
        fields = [
            "collaborator_id",
            "user_email",
            "diagram_id",
            "shared_to",
            "permission_level",
        ]

    def validate(self, attrs):
        attrs["diagram"] = self.context["diagram"]
        _ = CollaboratorValidator.validate_unique_collaborator(attrs)
        _ = CollaboratorValidator.validate_self_sharing(attrs)
        del attrs["diagram"]
        return attrs

    @staticmethod
    def validate_user_email(value):
        """
        Prevents sharing a diagram to an inactive user (is_active=0).
        """
        if not value.is_active:
            raise serializers.ValidationError(
                detail=f'User with the email "{value.email}" is not active.',
                code="inactive_user",
            )
        return value


# region @extend_schema_serializer
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Shared diagram example",
            summary="Response data example for diagram "
            "which was shared to another user",
            description="Value of **shared_to** field contains user's email "
            "who diagram was shared to.",
            response_only=True,
            value={
                "collaborator_id": f"{uuid.uuid4()}",
                "diagram_id": f"{uuid.uuid4()}",
                "diagram_title": "string",
                "shared_to": "user@example.com",
                "permission_level": PermissionLevels.VIEWONLY,
                "shared_at": datetime.now(timezone.utc).isoformat() + "Z",
            },
        ),
        OpenApiExample(
            name="Public diagram example",
            summary="Response data example for diagram which was shared publicly",
            description="Value of **shared_to** field is `null` (empty) "
            "for public diagrams.",
            response_only=True,
            value={
                "collaborator_id": f"{uuid.uuid4()}",
                "diagram_id": f"{uuid.uuid4()}",
                "diagram_title": "string",
                "shared_to": None,
                "permission_level": PermissionLevels.VIEWONLY,
                "shared_at": datetime.now(timezone.utc).isoformat() + "Z",
            },
        ),
    ]
)
# endregion
class CollaboratorSerializer(serializers.ModelSerializer):
    collaborator_id = serializers.ReadOnlyField(source="id")
    diagram_id = serializers.ReadOnlyField(source="diagram.id")
    diagram_title = serializers.ReadOnlyField(source="diagram.title")
    shared_to = serializers.ReadOnlyField(source="shared_to.email", allow_null=True)
    permission_level = serializers.ChoiceField(choices=PermissionLevels.CHOICES)

    class Meta:
        model = Collaborator
        fields = [
            "collaborator_id",
            "diagram_id",
            "diagram_title",
            "shared_to",
            "permission_level",
            "shared_at",
        ]
