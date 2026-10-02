from django.contrib import admin
from django.utils import timezone

from .models import InterviewExperience, InterviewQuestion


class QuestionInline(admin.TabularInline):
    model = InterviewQuestion
    extra = 0


@admin.register(InterviewExperience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("company", "year", "difficulty", "status", "created_at")
    list_filter = ("status", "company")
    inlines = [QuestionInline]
    actions = ["approve", "reject"]

    @admin.action(description="Approve selected experiences")
    def approve(self, request, qs):
        qs.update(status="approved", reviewed_by=request.user, reviewed_at=timezone.now())

    @admin.action(description="Reject selected experiences")
    def reject(self, request, qs):
        qs.update(status="rejected", reviewed_by=request.user, reviewed_at=timezone.now())
