from .models import Notification


def notify(user, kind, title, message="", drive=None, dedupe=False):
    """Create an in-app notification. dedupe=True avoids repeating the same kind for the same drive."""
    if dedupe and Notification.objects.filter(user=user, kind=kind, related_drive=drive).exists():
        return None
    return Notification.objects.create(user=user, kind=kind, title=title, message=message, related_drive=drive)
