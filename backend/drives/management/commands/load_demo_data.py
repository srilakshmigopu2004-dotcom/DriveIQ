"""Loads clearly-labelled FICTIONAL demo records so the UI can be tried. Remove with --clear."""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.core.management import call_command

from companies.models import Company, CompanyTechnology, JobRole, Skill
from drives.models import DriveRound, PlacementDrive
from users.models import College

PREFIX = "[DEMO] "


class Command(BaseCommand):
    help = "Create fictional demo company/drive data (names start with [DEMO]). NOT real companies."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Delete the demo records")

    def handle(self, *args, **opts):
        if opts["clear"]:
            Company.objects.filter(name__startswith=PREFIX).delete()
            College.objects.filter(name__startswith=PREFIX).delete()
            self.stdout.write("Demo data removed.")
            return
        call_command("seed_skills")
        college, _ = College.objects.get_or_create(name=PREFIX + "Sample Institute of Technology", defaults={"city": "Sample City"})
        sk = {s.name: s for s in Skill.objects.all()}
        today = date.today()
        specs = [
            ("Alpha Software", "Service", "Software Engineer Trainee", ["Python", "SQL", "OOP"], 6.0, 0, 7.0, 600000, 450000, 150000, 2, [("Aptitude Test", "aptitude", 1), ("Coding Test", "coding", 2), ("Technical Interview", "technical", 2), ("HR Interview", "hr", 1)]),
            ("Beta Analytics", "Product", "Data Analyst", ["SQL", "Python", "DBMS"], 7.5, 0, 6.0, 800000, None, None, None, [("Online Assessment", "aptitude", 2), ("Technical Interview", "technical", 3)]),
        ]
        for i, (name, cat, role, skills, cgpa, backlogs, _x, ctc, fixed, var, bond, rounds) in enumerate(specs):
            c, _ = Company.objects.get_or_create(name=PREFIX + name, defaults={
                "industry": "Software", "category": cat, "products_services": "Fictional demo company for testing DriveIQ.",
                "company_size": "Demo", "locations": "Sample City"})
            CompanyTechnology.objects.get_or_create(company=c, name="Demo tech")
            jr, _ = JobRole.objects.get_or_create(company=c, title=role)
            jr.required_skills.set([sk[s] for s in skills if s in sk])
            if PlacementDrive.objects.filter(company=c).exists():
                continue
            d = PlacementDrive.objects.create(
                company=c, college=college, job_role=jr, title=role, description="Fictional demo drive.",
                drive_date=today + timedelta(days=21 + 14 * i), application_deadline=today + timedelta(days=14 + 7 * i),
                status="registration_open", location="Sample City", openings=20, min_cgpa=cgpa, max_backlogs=backlogs,
                eligible_branches="CSE, IT", graduation_year=today.year + (1 if today.month > 6 else 0),
                ctc_total=ctc, ctc_fixed=fixed, ctc_variable=var, bond_years=bond, terms_notes="Demo terms.")
            d.required_skills.set([sk[s] for s in skills if s in sk])
            for n, (rn, rt, diff) in enumerate(rounds, 1):
                DriveRound.objects.create(drive=d, order=n, name=rn, round_type=rt, difficulty=diff)
        self.stdout.write("Demo data loaded. Everything named [DEMO] is fictional.")
