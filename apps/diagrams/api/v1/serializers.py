from rest_framework import serializers

from apps.diagrams.models import Diagram
from apps.users.models import User


class DiagramSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        write_only=True, required=False, queryset=User.objects.all()
    )

    class Meta:
        model = Diagram
        fields = "__all__"


class DiagramCopySerializer(DiagramSerializer):
    class Meta(DiagramSerializer.Meta):
        read_only_fields = ["title", "json"]
