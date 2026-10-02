from companies.models import SavedCompany
from drives.models import Application
from notifications.models import Notification
from preparation.models import PreparationTask

from .eligibility import check_eligibility
from .readiness import analyze_readiness
from .recommendations import drives_for, recommend
from .scoring import compute_match


def build_dashboard(profile):
    upcoming = []
    for d in drives_for(profile):
        elig = check_eligibility(profile, d)
        m = compute_match(profile, d, elig, analyze_readiness(profile, d))
        upcoming.append({"drive_id": d.id, "company": d.company.name, "title": d.title, "status": d.status,
                         "drive_date": d.drive_date, "eligible": elig["eligible"], "match_score": m["match_score"]})
    tasks = PreparationTask.objects.filter(plan__student=profile, is_done=False)[:8]
    return {
        "profile_complete": profile.is_complete,
        "upcoming_drives": upcoming,
        "eligible_count": sum(1 for u in upcoming if u["eligible"]),
        "readiness": analyze_readiness(profile),
        "recommended": recommend(profile, 3),
        "preparation_tasks": [{"id": t.id, "title": t.title, "week": t.week, "drive_id": t.plan.drive_id} for t in tasks],
        "saved_companies": [{"id": s.company_id, "name": s.company.name}
                            for s in SavedCompany.objects.filter(student=profile).select_related("company")],
        "applications": [{"drive_id": a.drive_id, "company": a.drive.company.name, "title": a.drive.title,
                          "status": a.status} for a in Application.objects.filter(student=profile)
                         .select_related("drive__company")],
        "recent_activity": [{"kind": n.kind, "title": n.title, "created_at": n.created_at}
                            for n in Notification.objects.filter(user=profile.user)[:5]],
    }
