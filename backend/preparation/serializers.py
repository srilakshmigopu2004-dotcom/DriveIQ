from rest_framework import serializers

from .models import PreparationPlan, PreparationTask


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreparationTask
        fields = ["id", "week", "focus", "area", "title", "is_done"]
        read_only_fields = ["week", "focus", "area", "title"]


class PlanSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = PreparationPlan
        fields = ["id", "drive", "created_at", "tasks"]
