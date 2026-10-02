from rest_framework import serializers

from .models import Application, DriveRound, PlacementDrive


class DriveRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriveRound
        fields = ["id", "drive", "order", "name", "round_type", "description", "duration_minutes", "difficulty"]


class DriveSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    college_name = serializers.CharField(source="college.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    rounds = DriveRoundSerializer(many=True, read_only=True)
    required_skill_names = serializers.SlugRelatedField(source="required_skills", many=True, read_only=True, slug_field="name")
    has_applied = serializers.SerializerMethodField()

    class Meta:
        model = PlacementDrive
        exclude = ["created_at"]

    def get_has_applied(self, obj):
        ids = self.context.get("applied_ids")
        return obj.id in ids if ids is not None else False

    def validate(self, attrs):
        d, dl = attrs.get("drive_date"), attrs.get("application_deadline")
        if d and dl and dl > d:
            raise serializers.ValidationError("Application deadline cannot be after the drive date.")
        fixed, var, total = attrs.get("ctc_fixed"), attrs.get("ctc_variable"), attrs.get("ctc_total")
        if total is not None and (fixed or 0) + (var or 0) > total:
            raise serializers.ValidationError("Fixed + variable pay cannot exceed total CTC.")
        return attrs


class ApplicationSerializer(serializers.ModelSerializer):
    company = serializers.CharField(source="drive.company.name", read_only=True)
    title = serializers.CharField(source="drive.title", read_only=True)

    class Meta:
        model = Application
        fields = ["id", "drive", "company", "title", "status", "created_at"]
