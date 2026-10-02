from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Certification, College, Internship, Project, StudentProfile, StudentSkill

User = get_user_model()
MAX_RESUME_BYTES = 2 * 1024 * 1024


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "full_name"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        probe = User(username=attrs.get("username"), email=attrs.get("email"))
        validate_password(attrs["password"], probe)
        return attrs

    def create(self, validated):
        full_name = validated.pop("full_name", "")
        user = User.objects.create_user(role=User.Role.STUDENT, **validated)  # role is never user-supplied
        StudentProfile.objects.create(user=user, full_name=full_name)
        return user


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ["id", "name", "city"]


class StudentSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)
    category = serializers.CharField(source="skill.category", read_only=True)

    class Meta:
        model = StudentSkill
        fields = ["id", "skill", "skill_name", "category", "level"]

    def validate_skill(self, value):
        return value


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "title", "description", "technologies"]


class InternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = ["id", "company_name", "role", "duration_months"]


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ["id", "name", "issuer"]


class ProfileSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source="college.name", read_only=True)
    skills_detail = StudentSkillSerializer(source="student_skills", many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    internships = InternshipSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    is_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ["id", "full_name", "college", "college_name", "degree", "branch", "graduation_year", "cgpa",
                  "backlogs", "dsa_level", "aptitude_level", "communication_level", "preferred_roles",
                  "preferred_locations", "resume", "is_complete", "skills_detail", "projects", "internships",
                  "certifications"]

    def validate_resume(self, f):
        if f and f.size > MAX_RESUME_BYTES:
            raise serializers.ValidationError("Resume must be 2 MB or smaller.")
        return f
