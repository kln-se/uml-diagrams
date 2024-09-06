import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.diagrams.models import Diagram
from apps.sharings.constants import PermissionLevels


class Collaborator(models.Model):
    """
    Model contains shared diagram and the user whom it was shared to.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shared_to = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="Shared to",
        help_text="User whom diagram is shared to.",
    )
    diagram = models.ForeignKey(
        Diagram,
        on_delete=models.CASCADE,
        help_text="Diagram which is shared.",
    )
    permission_level = models.CharField(
        max_length=16,
        choices=PermissionLevels.CHOICES,
        default=PermissionLevels.VIEWONLY,
        verbose_name="Permission level",
        help_text="Permission level which diagram is shared with.",
    )
    shared_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Shared at",
        help_text="Date and time when diagram was shared.",
    )

    class Meta:
        unique_together = ("shared_to", "diagram")

    def clean(self):
        """
        Prevents sharing a diagram to its owner.
        """
        if self.diagram.owner == self.shared_to:
            raise ValidationError(
                message=f'User with email "{self.shared_to.email}" cannot share the '
                f'diagram "{self.diagram.id}" to itself.',
                code="self_sharing",
            )
        super().clean()

    def __str__(self):
        return f"{self.diagram} 🡒 {self.shared_to} | {self.permission_level}"
