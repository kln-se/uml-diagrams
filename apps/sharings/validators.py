from typing import Dict

from rest_framework import serializers

from apps.sharings.models import Collaborator


class CollaboratorValidator:

    @staticmethod
    def validate_unique_collaborator(attrs: Dict) -> Dict:
        """
        Prevents sharing the same diagram to the same user.
        """
        if Collaborator.objects.filter(
            shared_to=attrs["shared_to"], diagram=attrs["diagram"]
        ).exists():
            raise serializers.ValidationError(
                detail=f'Diagram with id "{attrs["diagram"].id}" has already shared '
                f'to user with email "{attrs["shared_to"].email}".',
                code="non_unique_sharing",
            )
        return attrs

    @staticmethod
    def validate_self_sharing(attrs: Dict) -> Dict:
        """
        Prevents sharing a diagram to its owner.
        """
        diagram = attrs["diagram"]
        shared_to = attrs["shared_to"]
        if diagram.owner == shared_to:
            raise serializers.ValidationError(
                detail=f'User with email "{shared_to.email}" cannot share the '
                f'diagram "{diagram.id}" to itself.',
                code="self_sharing",
            )
        return attrs
