from rest_framework import generics, permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from matching.services.dashboard import build_dashboard

from .models import Certification, College, Internship, Project, StudentProfile, StudentSkill
from .permissions import ReadOnlyOrAdmin
from .serializers import (CertificationSerializer, CollegeSerializer, InternshipSerializer, MeSerializer,
                          ProfileSerializer, ProjectSerializer, RegisterSerializer, StudentSkillSerializer)


def get_profile(user):
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    return profile


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    def get(self, request):
        return Response(MeSerializer(request.user).data)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ["get", "patch", "put", "head", "options"]

    def get_object(self):
        return get_profile(self.request.user)


class OwnedViewSet(viewsets.ModelViewSet):
    """Base: rows always belong to the logged-in student's profile."""
    def get_queryset(self):
        return self.queryset.filter(student=get_profile(self.request.user))

    def perform_create(self, serializer):
        serializer.save(student=get_profile(self.request.user))


class SkillViewSet(OwnedViewSet):
    queryset = StudentSkill.objects.select_related("skill")
    serializer_class = StudentSkillSerializer


class ProjectViewSet(OwnedViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class InternshipViewSet(OwnedViewSet):
    queryset = Internship.objects.all()
    serializer_class = InternshipSerializer


class CertificationViewSet(OwnedViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer


class CollegeViewSet(viewsets.ModelViewSet):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = None


class DashboardView(APIView):
    def get(self, request):
        return Response(build_dashboard(get_profile(request.user)))
