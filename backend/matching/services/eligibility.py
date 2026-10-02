"""Eligibility checker: compares a student profile with a drive's hard criteria.

Returns a per-criterion breakdown with human-readable reasons (never a bare boolean).
A criterion the student's profile cannot answer (e.g. CGPA not filled) is reported as
'cannot verify' and counts as NOT confirmed eligible.
"""
from datetime import date

from .utils import csv_list


def _n(x):
    return str(float(x))  # 7.50 -> 7.5


def _check(name, passed, detail):
    return {"name": name, "passed": passed, "detail": detail}


def check_eligibility(profile, drive):
    checks, reasons = [], []

    if drive.min_cgpa is not None:
        if profile.cgpa is None:
            checks.append(_check("CGPA", False, f"Minimum CGPA is {_n(drive.min_cgpa)}; add your CGPA to your profile to verify."))
            reasons.append(f"Cannot verify CGPA (minimum {_n(drive.min_cgpa)}) because your CGPA is missing.")
        elif profile.cgpa >= drive.min_cgpa:
            checks.append(_check("CGPA", True, f"Your CGPA {_n(profile.cgpa)} meets the minimum of {_n(drive.min_cgpa)}."))
        else:
            msg = f"Minimum CGPA is {_n(drive.min_cgpa)} and your CGPA is {_n(profile.cgpa)}."
            checks.append(_check("CGPA", False, msg))
            reasons.append(f"Not eligible because minimum CGPA is {_n(drive.min_cgpa)} and your CGPA is {_n(profile.cgpa)}.")

    if drive.max_backlogs is not None:
        if profile.backlogs <= drive.max_backlogs:
            checks.append(_check("Backlogs", True, f"You have {profile.backlogs} backlog(s); up to {drive.max_backlogs} allowed."))
        else:
            checks.append(_check("Backlogs", False, f"Up to {drive.max_backlogs} backlog(s) allowed; you have {profile.backlogs}."))
            reasons.append(f"Not eligible because at most {drive.max_backlogs} backlog(s) are allowed and you have {profile.backlogs}.")

    branches = csv_list(drive.eligible_branches)
    if branches:
        if not profile.branch:
            checks.append(_check("Branch", False, "Add your branch to your profile to verify."))
            reasons.append("Cannot verify branch because your branch is missing.")
        elif profile.branch.strip().lower() in branches:
            checks.append(_check("Branch", True, f"Your branch ({profile.branch}) is in the eligible list."))
        else:
            checks.append(_check("Branch", False, f"Eligible branches: {drive.eligible_branches}. Your branch: {profile.branch}."))
            reasons.append(f"Not eligible because your branch ({profile.branch}) is not in the eligible list: {drive.eligible_branches}.")

    if drive.graduation_year is not None:
        if profile.graduation_year is None:
            checks.append(_check("Graduation year", False, "Add your graduation year to your profile to verify."))
            reasons.append("Cannot verify graduation year because it is missing.")
        elif profile.graduation_year == drive.graduation_year:
            checks.append(_check("Graduation year", True, f"Graduation year {profile.graduation_year} matches."))
        else:
            checks.append(_check("Graduation year", False, f"Drive is for the {drive.graduation_year} batch; yours is {profile.graduation_year}."))
            reasons.append(f"Not eligible because this drive is for the {drive.graduation_year} batch and you graduate in {profile.graduation_year}.")

    # Skills are advisory: real drives rarely filter on skills, but gaps matter for preparation.
    have = {s.name.lower() for s in profile.skills.all()}
    required = list(drive.required_skills.all())
    missing = [s.name for s in required if s.name.lower() not in have]

    registration_open = drive.status == "registration_open" and (
        drive.application_deadline is None or drive.application_deadline >= date.today())
    if registration_open:
        reg_note = "Registration is open."
    elif drive.status == "cancelled":
        reg_note = "This drive is cancelled."
    elif drive.status in ("completed", "ongoing"):
        reg_note = f"This drive is {drive.get_status_display().lower()}; registration is closed."
    elif drive.status == "registration_open":
        reg_note = "The application deadline has passed."
    else:
        reg_note = "Registration has not opened yet."

    eligible = all(c["passed"] for c in checks)
    return {
        "drive_id": drive.id,
        "eligible": eligible,
        "verdict": "Eligible" if eligible else "Not Eligible",
        "reasons": reasons,
        "checks": checks,
        "skill_gaps": missing,
        "registration_open": registration_open,
        "registration_note": reg_note,
        "profile_incomplete": not profile.is_complete,
    }
