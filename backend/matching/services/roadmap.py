"""Personalised roadmap built from the student's weak areas and the drive's rounds."""
import math
from datetime import date

from .readiness import AREA_LABEL, analyze_readiness

TOPICS = {
    "aptitude": ["Quantitative aptitude: percentages, ratios, time & work", "Logical reasoning and puzzles",
                 "Verbal ability and reading comprehension"],
    "dsa": ["Arrays and strings", "Searching and sorting", "Linked lists, stacks and queues",
            "Recursion and basic trees", "Solve timed coding problems"],
    "sql": ["SELECT, WHERE, GROUP BY, ORDER BY", "Joins and subqueries", "Keys and normalisation"],
    "programming": ["Core language fundamentals", "OOP concepts (inheritance, polymorphism, encapsulation)"],
    "communication": ["Self-introduction and common HR questions", "Group discussion practice", "Mock HR interview"],
    "projects": ["Prepare a 2-minute explanation of each project (problem, stack, your role, challenges)",
                 "Revise resume line by line"],
}


def build_roadmap(profile, drive):
    ready = analyze_readiness(profile, drive)
    days = (drive.drive_date - date.today()).days if drive.drive_date else None
    total_weeks = 4 if days is None or days >= 28 else max(1, math.ceil(max(days, 1) / 7))
    content_weeks = total_weeks - 1

    used = sorted([a for a in ready["areas"] if a["relevant"]], key=lambda a: a["score"])
    focus_areas = [a for a in used if a["level"] < 3] or used[:1]

    weeks = []
    for i in range(content_weeks):
        chunk = focus_areas[i::content_weeks]
        tasks = [{"area": a["key"], "title": t} for a in chunk for t in TOPICS[a["key"]][:3]]
        weeks.append({"week": i + 1, "focus": ", ".join(a["label"] for a in chunk) or "Revision", "tasks": tasks})

    final = [{"area": "communication", "title": "Take at least one full mock interview"},
             {"area": "company", "title": f"Read the {drive.company.name} profile, job description and approved previous experiences"}]
    req = [s.name for s in drive.required_skills.all()]
    if req:
        final.append({"area": "company", "title": "Revise required skills: " + ", ".join(req)})
    weeks.append({"week": total_weeks, "focus": "Mock interviews & company-specific preparation", "tasks": final})
    return {"total_weeks": total_weeks, "based_on": ready["classification"], "weeks": weeks,
            "note": "Generated from your self-reported levels and this drive's listed rounds."}
