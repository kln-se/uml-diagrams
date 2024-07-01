from rest_framework import serializers

from apps.diagrams.models import Diagram


class DiagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagram
        fields = "__all__"


class DiagramCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagram
        fields = "__all__"
        read_only_fields = ["title", "json"]
