from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        NEW_DRIVE = "new_drive", "New drive"
        DEADLINE = "deadline", "Registration deadline"
        DRIVE_DATE = "drive_date", "Drive date reminder"
        ELIGIBILITY = "eligibility", "Eligibility update"
        PREPARATION = "preparation", "Preparation reminder"
        EXPERIENCE = "experience", "New previous-drive experience"
        OFFER_WARNING = "offer_warning", "Offer-term warning"
        SYSTEM = "system", "System"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.SYSTEM)
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    related_drive = models.ForeignKey("drives.PlacementDrive", null=True, blank=True, on_delete=models.SET_NULL)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
