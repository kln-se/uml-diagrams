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

    class Meta:
        model = Collaborator
        fields = [
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
