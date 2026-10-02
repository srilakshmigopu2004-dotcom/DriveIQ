from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from companies.models import SavedCompany
from notifications.models import Notification
from notifications.services import notify
from users.permissions import IsAdminRole

from .models import InterviewExperience
from .serializers import ExperienceSerializer


class ExperienceViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = ExperienceSerializer

    def get_queryset(self):
        qs = InterviewExperience.objects.select_related("company").prefetch_related("questions")
        if self.action in ("pending", "moderate"):
            return qs
        user = self.request.user
        # students see approved items + their own; moderation queue is admin-only
        qs = qs.filter(status="approved") | qs.filter(author=user)
        p = self.request.query_params
        if p.get("company"):
            qs = qs.filter(company_id=p["company"])
        if p.get("drive"):
            qs = qs.filter(drive_id=p["drive"])
        return qs.distinct()

    def get_permissions(self):
        if self.action in ("pending", "moderate"):
            return [IsAdminRole()]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author_id != request.user.id and not request.user.is_admin_role:
            return Response({"detail": "You can only delete your own experience."}, status=403)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        data = self.get_serializer(self.get_queryset().filter(status="pending"), many=True).data
        return Response(data)

    @action(detail=True, methods=["post"])
    def moderate(self, request, pk=None):
        exp = self.get_object()
        decision = request.data.get("action")
        if decision not in ("approve", "reject"):
            return Response({"detail": "action must be 'approve' or 'reject'."}, status=400)
        exp.status = "approved" if decision == "approve" else "rejected"
        exp.reviewed_by, exp.reviewed_at = request.user, timezone.now()
        exp.save()
        if exp.status == "approved":
            notify(exp.author, Notification.Kind.EXPERIENCE, "Your experience was approved",
                   f"Your {exp.company.name} experience is now visible to other students.")
            for sc in SavedCompany.objects.filter(company=exp.company).select_related("student__user"):
                notify(sc.student.user, Notification.Kind.EXPERIENCE, f"New experience: {exp.company.name}",
                       "A new previous-drive experience was added for a company you saved.")
        return Response({"status": exp.status})
