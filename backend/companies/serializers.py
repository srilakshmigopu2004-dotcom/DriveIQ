from rest_framework import serializers

from .models import Company, CompanyTechnology, JobRole, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "category"]


class JobRoleSerializer(serializers.ModelSerializer):
    required_skill_names = serializers.SlugRelatedField(source="required_skills", many=True, read_only=True, slug_field="name")

    class Meta:
        model = JobRole
        fields = ["id", "company", "title", "description", "required_skills", "required_skill_names"]


class CompanySerializer(serializers.ModelSerializer):
    technologies = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    roles = JobRoleSerializer(many=True, read_only=True)
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ["id", "name", "logo_url", "industry", "category", "products_services", "company_size", "locations",
                  "careers_url", "campus_hiring_info", "typical_selection_process", "ctc_information",
                  "important_requirements", "technologies", "roles", "is_saved"]

    def get_is_saved(self, obj):
        saved = self.context.get("saved_ids")
        return obj.id in saved if saved is not None else False
