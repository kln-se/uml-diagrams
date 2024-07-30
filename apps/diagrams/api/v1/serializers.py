from rest_framework import serializers

from apps.diagrams.models import Diagram
from apps.users.models import User


class DiagramSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        write_only=True, required=False, queryset=User.objects.all()
    )
    email = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Diagram
        fields = "__all__"


class DiagramCopySerializer(DiagramSerializer):
    class Meta(DiagramSerializer.Meta):
        read_only_fields = ["title", "json"]


class DiagramListSerializer(DiagramSerializer):
    """
    Used to list diagrams via GET api/v1/diagrams/
    """

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta(DiagramSerializer.Meta):
        fields = ["id", "title", "owner", "email", "created_at", "updated_at"]
