"""Rule-based preparation readiness (transparent; ML version is documented in /ml)."""

LEVEL_LABEL = {1: "Beginner", 2: "Intermediate", 3: "Strong"}

AREA_LABEL = {
    "dsa": "DSA", "aptitude": "Aptitude", "communication": "Communication",
    "projects": "Projects & experience", "sql": "SQL", "programming": "Programming languages",
}
# Which areas each round type exercises
ROUND_AREAS = {
    "aptitude": ["aptitude"],
    "coding": ["dsa", "programming"],
    "technical": ["dsa", "sql", "projects", "programming"],
    "hr": ["communication", "projects"],
    "gd": ["communication"],
}


def _skill_level(profile, name):
    for ss in profile.student_skills.select_related("skill"):
        if ss.skill.name.lower() == name:
            return ss.level
    return 1


def area_levels(profile):
    pts = profile.projects.count() + 2 * profile.internships.count()
    projects = 1 if pts == 0 else (2 if pts <= 2 else 3)
    lang_levels = [ss.level for ss in profile.student_skills.select_related("skill")
                   if ss.skill.category == "language"]
    programming = round(sum(lang_levels) / len(lang_levels)) if lang_levels else 1
    return {
        "dsa": profile.dsa_level, "aptitude": profile.aptitude_level,
        "communication": profile.communication_level, "projects": projects,
        "sql": _skill_level(profile, "sql"), "programming": programming,
    }


def relevant_areas(drive):
    if drive is None:
        return list(AREA_LABEL)
    keys = []
    for r in drive.rounds.all():
        for a in ROUND_AREAS.get(r.round_type, []):
            if a not in keys:
                keys.append(a)
    return keys or list(AREA_LABEL)


def analyze_readiness(profile, drive=None):
    levels = area_levels(profile)
    relevant = relevant_areas(drive)
    areas = [{"key": k, "label": AREA_LABEL[k], "level": levels[k], "level_label": LEVEL_LABEL[levels[k]],
              "score": round(levels[k] / 3 * 100), "relevant": k in relevant} for k in AREA_LABEL]
    used = [a for a in areas if a["relevant"]]
    overall = round(sum(a["score"] for a in used) / len(used))
    classification = "Needs Preparation" if overall < 50 else ("Nearly Ready" if overall < 80 else "Ready")
    strengths = [a["label"] for a in used if a["level"] == 3]
    weak = [a["label"] for a in sorted(used, key=lambda a: a["score"]) if a["level"] < 3]
    return {
        "overall": overall, "classification": classification, "areas": areas,
        "strengths": strengths, "recommended_focus": weak,
        "method": "rule-based: self-reported levels (Beginner=33, Intermediate=67, Strong=100) averaged over the areas "
                  "this drive's rounds test. Thresholds: <50 Needs Preparation, <80 Nearly Ready, else Ready.",
    }
