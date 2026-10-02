from django.db import models


class PreparationPlan(models.Model):
    student = models.ForeignKey("users.StudentProfile", on_delete=models.CASCADE, related_name="plans")
    drive = models.ForeignKey("drives.PlacementDrive", on_delete=models.CASCADE, related_name="plans")
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "drive")


class PreparationTask(models.Model):
    plan = models.ForeignKey(PreparationPlan, on_delete=models.CASCADE, related_name="tasks")
    week = models.PositiveSmallIntegerField()
    focus = models.CharField(max_length=150, blank=True)
    area = models.CharField(max_length=40, blank=True)
    title = models.CharField(max_length=250)
    is_done = models.BooleanField(default=False)

    class Meta:
        ordering = ["week", "id"]
