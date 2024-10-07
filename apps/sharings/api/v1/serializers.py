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


class CollaboratorSerializer(serializers.ModelSerializer):
    collaborator_id = serializers.ReadOnlyField(source="id")
    diagram_id = serializers.ReadOnlyField(source="diagram.id")
    shared_to = serializers.ReadOnlyField(source="shared_to.email")
    permission_level = serializers.ChoiceField(choices=PermissionLevels.CHOICES)

    class Meta:
        model = Collaborator
        fields = [
            "collaborator_id",
            "diagram_id",
            "shared_to",
            "permission_level",
            "shared_at",
        ]
