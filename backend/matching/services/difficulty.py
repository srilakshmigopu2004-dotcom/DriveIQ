"""Transparent drive difficulty. Every factor is listed; factors with no data are skipped, never guessed."""
LABEL = {1: "low", 2: "medium", 3: "high"}


def analyze_difficulty(drive):
    from experiences.models import InterviewExperience  # local import avoids circular dependency
    factors = []
    rounds = list(drive.rounds.all())
    if rounds:
        n = len(rounds)
        lvl = 1 if n <= 2 else (2 if n == 3 else 3)
        factors.append({"name": "Number of rounds", "level": lvl, "detail": f"{n} round(s) listed."})
        for r in rounds:
            if r.difficulty:
                factors.append({"name": f"{r.name} difficulty", "level": r.difficulty,
                                "detail": f"Round rated {LABEL[r.difficulty]} difficulty in drive data."})
    hist = list(InterviewExperience.objects.filter(company=drive.company, status="approved")
                .values_list("difficulty", flat=True))
    if hist:
        avg = sum(hist) / len(hist)
        lvl = 1 if avg <= 2 else (2 if avg <= 3.5 else 3)
        factors.append({"name": "Previous student experiences", "level": lvl,
                        "detail": f"Average difficulty {avg:.1f}/5 from {len(hist)} approved experience(s)."})
    apps = drive.applications.count()
    if drive.openings and apps:
        ratio = apps / drive.openings
        lvl = 1 if ratio <= 5 else (2 if ratio <= 15 else 3)
        factors.append({"name": "Competition (DriveIQ registrations per opening)", "level": lvl,
                        "detail": f"{apps} registration(s) for {drive.openings} opening(s) on DriveIQ only."})
    if not factors:
        return {"label": "Insufficient data", "average": None, "factors": [],
                "note": "No rounds, ratings or approved experiences are available yet, so no assessment is made."}
    avg = sum(f["level"] for f in factors) / len(factors)
    label = "Easy" if avg < 1.7 else ("Moderate" if avg < 2.4 else "High")
    note = f"Based on {len(factors)} factor(s): average level {avg:.1f} of 3."
    if len(factors) < 3:
        note += " Limited data, so treat this as a rough indication."
    return {"label": label, "average": round(avg, 2), "factors": [
        {**f, "level_label": LABEL[f["level"]]} for f in factors], "note": note}
