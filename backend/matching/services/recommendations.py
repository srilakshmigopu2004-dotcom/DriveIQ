from drives.models import PlacementDrive

from .eligibility import check_eligibility
from .readiness import analyze_readiness
from .scoring import compute_match

OPEN_STATUSES = ["upcoming", "registration_open", "ongoing"]


def drives_for(profile, statuses=None):
    qs = PlacementDrive.objects.select_related("company", "college", "job_role") \
        .prefetch_related("required_skills", "rounds") \
        .filter(status__in=statuses or OPEN_STATUSES)
    if profile.college_id:
        qs = qs.filter(college_id=profile.college_id)
    return qs


def recommend(profile, limit=5):
    results = []
    for drive in drives_for(profile):
        elig = check_eligibility(profile, drive)
        if not elig["eligible"]:
            continue
        m = compute_match(profile, drive, elig, analyze_readiness(profile, drive))
        results.append({"drive_id": drive.id, "title": drive.title, "company": drive.company.name,
                        "drive_date": drive.drive_date, "match_score": m["match_score"],
                        "why": m["strengths"][:2] or ["You meet all eligibility criteria."],
                        "improve": m["improvements"][:2]})
    results.sort(key=lambda r: -r["match_score"])
    return results[:limit]
