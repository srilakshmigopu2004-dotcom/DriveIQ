from django.db import transaction
from rest_framework import serializers

from .models import InterviewExperience, InterviewQuestion


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = ["id", "round_name", "text", "topic"]


class ExperienceSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    company_name = serializers.CharField(source="company.name", read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = InterviewExperience
        fields = ["id", "company", "company_name", "drive", "year", "difficulty", "rounds_count", "duration_minutes",
                  "summary", "status", "questions", "created_at", "is_mine"]
        read_only_fields = ["status", "created_at"]  # author is anonymous in API output

    def get_is_mine(self, obj):
        r = self.context.get("request")
        return bool(r and obj.author_id == r.user.id)

    def validate_summary(self, v):
        if len(v.strip()) < 20:
            raise serializers.ValidationError("Please write at least 20 characters.")
        if len(v) > 5000:
            raise serializers.ValidationError("Summary is too long (max 5000 characters).")
        return v

    @transaction.atomic
    def create(self, validated):
        questions = validated.pop("questions", [])
        exp = InterviewExperience.objects.create(author=self.context["request"].user, **validated)
        InterviewQuestion.objects.bulk_create([InterviewQuestion(experience=exp, **q) for q in questions])
        return exp
