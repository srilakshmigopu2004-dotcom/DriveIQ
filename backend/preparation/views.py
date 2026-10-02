from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from drives.models import PlacementDrive
from matching.services.readiness import analyze_readiness
from matching.services.roadmap import build_roadmap
from users.views import get_profile

from .models import PreparationPlan, PreparationTask
from .serializers import PlanSerializer, TaskSerializer


class ReadinessView(APIView):
    def get(self, request):
        profile = get_profile(request.user)
        drive_id = request.query_params.get("drive")
        drive = get_object_or_404(PlacementDrive, pk=drive_id) if drive_id else None
        return Response(analyze_readiness(profile, drive))


class RoadmapView(APIView):
    """GET: preview a roadmap (not saved). POST: generate and save it as a trackable plan."""
    def _drive(self, drive_id):
        return get_object_or_404(PlacementDrive.objects.select_related("company").prefetch_related("rounds", "required_skills"),
                                 pk=drive_id)

    def get(self, request, drive_id):
        profile = get_profile(request.user)
        drive = self._drive(drive_id)
        data = build_roadmap(profile, drive)
        plan = PreparationPlan.objects.filter(student=profile, drive=drive).first()
        data["saved_plan"] = PlanSerializer(plan).data if plan else None
        return Response(data)

    def post(self, request, drive_id):
        profile = get_profile(request.user)
        drive = self._drive(drive_id)
        data = build_roadmap(profile, drive)
        plan, _ = PreparationPlan.objects.get_or_create(student=profile, drive=drive)
        plan.tasks.all().delete()
        PreparationTask.objects.bulk_create([
            PreparationTask(plan=plan, week=w["week"], focus=w["focus"], area=t["area"], title=t["title"])
            for w in data["weeks"] for t in w["tasks"]])
        plan.save()
        return Response(PlanSerializer(plan).data, status=201)


class TaskUpdateView(generics.UpdateAPIView):
    serializer_class = TaskSerializer
    http_method_names = ["patch", "put", "options"]

    def get_queryset(self):
        return PreparationTask.objects.filter(plan__student=get_profile(self.request.user))
