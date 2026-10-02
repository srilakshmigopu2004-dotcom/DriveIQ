from datetime import date, timedelta

from django.core.management.base import BaseCommand

from drives.models import Application, PlacementDrive
from matching.services.eligibility import check_eligibility
from notifications.models import Notification
from notifications.services import notify
from users.models import StudentProfile


class Command(BaseCommand):
    help = "Create in-app deadline and drive-date reminders. Run daily (cron / Task Scheduler)."

    def handle(self, *args, **opts):
        today, soon = date.today(), date.today() + timedelta(days=2)
        count = 0
        for d in PlacementDrive.objects.filter(status="registration_open", application_deadline__range=(today, soon)):
            applied = set(d.applications.values_list("student_id", flat=True))
            for p in StudentProfile.objects.filter(college=d.college).select_related("user"):
                if p.id in applied or not check_eligibility(p, d)["eligible"]:
                    continue
                if notify(p.user, Notification.Kind.DEADLINE, f"Deadline soon: {d.company.name}",
                          f"Registration for {d.title} closes on {d.application_deadline}.", d, dedupe=True):
                    count += 1
        tomorrow = today + timedelta(days=1)
        for a in Application.objects.filter(drive__drive_date__range=(today, tomorrow)).select_related("student__user", "drive__company"):
            if notify(a.student.user, Notification.Kind.DRIVE_DATE, f"Drive on {a.drive.drive_date}: {a.drive.company.name}",
                      "Your drive is coming up. Check your preparation roadmap.", a.drive, dedupe=True):
                count += 1
        self.stdout.write(f"Created {count} reminder(s).")
