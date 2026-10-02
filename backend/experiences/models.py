from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class InterviewExperience(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="experiences")
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE, related_name="experiences")
    drive = models.ForeignKey("drives.PlacementDrive", null=True, blank=True, on_delete=models.SET_NULL,
                              related_name="experiences")
    year = models.PositiveIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    difficulty = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rounds_count = models.PositiveSmallIntegerField(default=1)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    summary = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="reviewed_experiences")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class InterviewQuestion(models.Model):
    experience = models.ForeignKey(InterviewExperience, on_delete=models.CASCADE, related_name="questions")
    round_name = models.CharField(max_length=100, blank=True)
    text = models.TextField()
    topic = models.CharField(max_length=100, blank=True)
