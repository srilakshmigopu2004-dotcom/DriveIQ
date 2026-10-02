from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import ReadOnlyOrAdmin
from users.views import get_profile

from .models import Company, JobRole, SavedCompany, Skill
from .serializers import CompanySerializer, JobRoleSerializer, SkillSerializer


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [ReadOnlyOrAdmin]
    pagination_class = None


class JobRoleViewSet(viewsets.ModelViewSet):
    queryset = JobRole.objects.select_related("company").prefetch_related("required_skills")
    serializer_class = JobRoleSerializer
    permission_classes = [ReadOnlyOrAdmin]


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        qs = Company.objects.prefetch_related("technologies", "roles__required_skills")
        q = self.request.query_params.get("search")
        if q:
            qs = qs.filter(name__icontains=q)
        industry = self.request.query_params.get("industry")
        if industry:
            qs = qs.filter(industry__iexact=industry)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.request.user.is_authenticated:
            ctx["saved_ids"] = set(SavedCompany.objects.filter(student=get_profile(self.request.user))
                                   .values_list("company_id", flat=True))
        return ctx

    @action(detail=True, methods=["post", "delete"], url_path="save", permission_classes=[IsAuthenticated])
    def save_company(self, request, pk=None):
        company = self.get_object()
        profile = get_profile(request.user)
        if request.method == "POST":
            SavedCompany.objects.get_or_create(student=profile, company=company)
        else:
            SavedCompany.objects.filter(student=profile, company=company).delete()
        return Response({"saved": request.method == "POST"})
