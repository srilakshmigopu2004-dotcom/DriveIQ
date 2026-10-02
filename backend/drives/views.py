from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matching.services.difficulty import analyze_difficulty
from matching.services.eligibility import check_eligibility
from notifications.models import Notification
from notifications.services import notify
from users.permissions import ReadOnlyOrAdmin
from users.views import get_profile

from .models import Application, DriveRound, PlacementDrive
from .serializers import ApplicationSerializer, DriveRoundSerializer, DriveSerializer


class DriveViewSet(viewsets.ModelViewSet):
    serializer_class = DriveSerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        qs = PlacementDrive.objects.select_related("company", "college", "job_role") \
            .prefetch_related("rounds", "required_skills")
        p = self.request.query_params
        if p.get("status"):
            qs = qs.filter(status=p["status"])
        if p.get("company"):
            qs = qs.filter(company_id=p["company"])
        if p.get("college"):
            qs = qs.filter(college_id=p["college"])
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.request.user.is_authenticated:
            ctx["applied_ids"] = set(Application.objects.filter(student=get_profile(self.request.user))
                                     .values_list("drive_id", flat=True))
        return ctx

    @action(detail=True, methods=["get"])
    def difficulty(self, request, pk=None):
        return Response(analyze_difficulty(self.get_object()))

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def apply(self, request, pk=None):
        drive = self.get_object()
        profile = get_profile(request.user)
        elig = check_eligibility(profile, drive)
        if not elig["registration_open"]:
            return Response({"detail": elig["registration_note"]}, status=400)
        if not elig["eligible"]:
            return Response({"detail": "You are not eligible for this drive.", "reasons": elig["reasons"]}, status=400)
        app, created = Application.objects.get_or_create(student=profile, drive=drive)
        if created:
            notify(request.user, Notification.Kind.SYSTEM, f"Applied: {drive.company.name}",
                   f"Your application for {drive.title} was recorded.", drive)
        return Response(ApplicationSerializer(app).data, status=201 if created else 200)


class RoundViewSet(viewsets.ModelViewSet):
    queryset = DriveRound.objects.all()
    serializer_class = DriveRoundSerializer
    permission_classes = [ReadOnlyOrAdmin]


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(student=get_profile(self.request.user)).select_related("drive__company")
