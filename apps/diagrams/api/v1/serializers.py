from rest_framework import serializers

from apps.diagrams.models import Diagram


class DiagramSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Diagram
        fields = "__all__"


class DiagramCopySerializer(DiagramSerializer):
    class Meta(DiagramSerializer.Meta):
        read_only_fields = ["title", "json"]
