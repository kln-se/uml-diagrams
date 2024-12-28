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

    @staticmethod
    def validate_multiple_public_shares(attrs: Dict) -> Dict:
        """
        Prevents multiple public shares for the same diagram.
        Partly intersects with the `clean()` method of Collaborator model
        by functionality, because model validation by `clean()` is
        not invoked by default, so it should be done manually
        inside serializer validate().
        """
        diagram = attrs["diagram"]
        if Collaborator.objects.filter(diagram=diagram, shared_to=None).exists():
            raise serializers.ValidationError(
                detail=f"Cannot create multiple public shares for the same object: "
                f"diagram {diagram.id} has already been shared publicly.",
                code="multiple_public_shares",
            )
        return attrs
