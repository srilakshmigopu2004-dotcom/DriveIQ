"""Student-company match score = PROFILE ALIGNMENT, not a chance of selection."""
from .eligibility import check_eligibility
from .readiness import analyze_readiness
from .utils import csv_list

WEIGHTS = {"eligibility": 0.30, "skills": 0.30, "role": 0.15, "location": 0.05, "readiness": 0.20}
DISCLAIMER = ("This score shows how well your profile aligns with the role and drive details we have. "
              "It is NOT a prediction or guarantee of selection.")


def _factor(key, label, score, explanation):
    return {"key": key, "label": label, "score": score,
            "weight": WEIGHTS[key] if score is not None else 0, "explanation": explanation}


def compute_match(profile, drive, eligibility=None, readiness=None):
    elig = eligibility or check_eligibility(profile, drive)
    ready = readiness or analyze_readiness(profile, drive)
    factors = []

    if elig["checks"]:
        passed = sum(1 for c in elig["checks"] if c["passed"])
        factors.append(_factor("eligibility", "Eligibility", round(passed / len(elig["checks"]) * 100),
                               f"{passed} of {len(elig['checks'])} eligibility criteria satisfied."))
    else:
        factors.append(_factor("eligibility", "Eligibility", 100, "No restrictions specified for this drive."))

    required = [s.name for s in drive.required_skills.all()]
    if required:
        have = {s.name.lower() for s in profile.skills.all()}
        matched = [n for n in required if n.lower() in have]
        factors.append(_factor("skills", "Skills", round(len(matched) / len(required) * 100),
                               f"You list {len(matched)} of {len(required)} required skills"
                               + (f" ({', '.join(matched)})." if matched else ".")))
    else:
        factors.append(_factor("skills", "Skills", None, "No required skills listed for this drive, so skills are not scored."))

    prefs = csv_list(profile.preferred_roles)
    role_text = f"{drive.title} {drive.job_role.title if drive.job_role else ''}".lower()
    if prefs:
        hit = any(p in role_text or (drive.title and drive.title.lower() in p) for p in prefs)
        factors.append(_factor("role", "Role preference", 100 if hit else 0,
                               "This role matches one of your preferred roles." if hit
                               else "This role is not among your preferred roles."))
    else:
        factors.append(_factor("role", "Role preference", None, "Add preferred roles to your profile to score this."))

    locs = csv_list(profile.preferred_locations)
    if locs and drive.location:
        hit = any(l in drive.location.lower() or drive.location.lower() in l for l in locs)
        factors.append(_factor("location", "Location preference", 100 if hit else 0,
                               "Location matches your preference." if hit else "Location is not in your preferred list."))
    else:
        factors.append(_factor("location", "Location preference", None,
                               "Add preferred locations (and the drive needs a location) to score this."))

    factors.append(_factor("readiness", "Preparation readiness", ready["overall"],
                           f"Readiness for this drive's rounds: {ready['classification']}."))

    total_w = sum(f["weight"] for f in factors)
    score = round(sum(f["weight"] * f["score"] for f in factors if f["score"] is not None) / total_w)

    strengths = [f"{f['label']}: {f['explanation']}" for f in factors if f["score"] is not None and f["score"] >= 70]
    improvements = [f"Improve {x}" for x in ready["recommended_focus"][:3]]
    if elig["skill_gaps"]:
        improvements.append("Learn or add required skills: " + ", ".join(elig["skill_gaps"]))
    for r in elig["reasons"]:
        improvements.append(r)

    return {"drive_id": drive.id, "match_score": score, "factors": factors, "strengths": strengths,
            "improvements": improvements, "eligibility": elig, "readiness": ready, "disclaimer": DISCLAIMER}
