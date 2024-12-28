import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

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
        null=True,
        blank=True,
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
        constraints = [
            # Prevents sharing diagram as public with other than "view-only" permission.
            # This is reinsurance during diagram sharing via admin panel because
            # public sharing via endpoint automatically uses "view-only" permission.
            models.CheckConstraint(
                check=Q(shared_to__isnull=True, permission_level="view-only")
                | Q(shared_to__isnull=False),
                name="shared_to_is_null_when_permission_level_is_not_view_only",
                violation_error_message="The 'shared_to' field may only \
                be empty if the 'permission_level' field is set to 'view-only' (View).",
                violation_error_code="wrong_permission_level_for_null_shared_to_field",
            )
        ]

    def clean(self):
        """
        This method is used by model validation during its creation via admin panel.
        Nowhere else it is used, because neither serializer.save() nor model.create()
        framework methods invoke it by default.
        """
        # Check that 'diagram' field is not None before proceeding and
        # excluding other fields from validation.
        self.clean_fields(exclude={"id", "shared_to", "permission_level", "shared_at"})
        # Prevents sharing a diagram to its owner.
        if self.diagram.owner == self.shared_to:
            raise ValidationError(
                message=f'User with email "{self.shared_to.email}" cannot share the '
                f'diagram "{self.diagram.id}" to itself.',
                code="self_sharing",
            )
        # Prevents multiple public shares for the same diagram.
        elif (
            self.shared_to is None
            and Collaborator.objects.filter(
                diagram=self.diagram, shared_to=None
            ).exists()
        ):
            raise ValidationError(
                message=f"Cannot create multiple public shares for the same object:\n"
                f"diagram {self.diagram.id} has already been shared publicly.",
                code="multiple_public_shares",
            )
        super().clean()

    def __str__(self):
        return f"{self.diagram} 🡒 {self.shared_to} | {self.permission_level}"
