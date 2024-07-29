import uuid

from django.contrib.auth import get_user_model
from django.db import models


class Diagram(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=255, null=False, blank=False, verbose_name="Diagram title"
    )
    json = models.JSONField(
        null=False,
        blank=False,
        verbose_name="Diagram JSON",
        help_text="Diagram structure and properties in JSON format.",
    )
    description = models.TextField(
        blank=True, default="", verbose_name="Diagram description"
    )
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Contributor",
        help_text="User who added this diagram to the database.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    def __str__(self):
        return f'Diagram: "{self.title}"'

    class Meta:
        verbose_name = "Diagram"
        verbose_name_plural = "Diagrams"
