from django.core.management.base import BaseCommand

from companies.models import Skill

SKILLS = [
    ("Python", "language"), ("Java", "language"), ("C", "language"), ("C++", "language"), ("JavaScript", "language"),
    ("SQL", "database"), ("MySQL", "database"), ("PostgreSQL", "database"), ("MongoDB", "database"),
    ("Django", "framework"), ("React", "framework"), ("Spring Boot", "framework"), ("Node.js", "framework"),
    ("Data Structures", "concept"), ("Algorithms", "concept"), ("OOP", "concept"), ("DBMS", "concept"),
    ("Operating Systems", "concept"), ("Computer Networks", "concept"), ("Git", "tool"),
]


class Command(BaseCommand):
    help = "Create a neutral list of common skills (no company data)."

    def handle(self, *args, **opts):
        n = sum(Skill.objects.get_or_create(name=name, defaults={"category": cat})[1] for name, cat in SKILLS)
        self.stdout.write(f"Added {n} skill(s).")
