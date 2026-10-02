from django.db.models.signals import post_save
from django.dispatch import receiver

from matching.services.eligibility import check_eligibility
from notifications.models import Notification
from notifications.services import notify
from users.models import StudentProfile

from .models import PlacementDrive


@receiver(post_save, sender=PlacementDrive)
def notify_eligible_students(sender, instance, created, **kwargs):
    """New drive -> in-app notification for eligible students of that college."""
    if not created or instance.status not in ("upcoming", "registration_open"):
        return
    for p in StudentProfile.objects.filter(college=instance.college).select_related("user"):
        if check_eligibility(p, instance)["eligible"]:
            notify(p.user, Notification.Kind.NEW_DRIVE, f"New drive: {instance.company.name}",
                   f"{instance.title} - you appear eligible. Open the drive for details.", instance)
