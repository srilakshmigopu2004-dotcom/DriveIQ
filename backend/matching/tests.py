from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from companies.models import Company, Skill
from drives.models import DriveRound, PlacementDrive
from experiences.models import InterviewExperience
from matching.services.eligibility import check_eligibility
from matching.services.scoring import compute_match
from matching.services.utils import format_inr
from notifications.models import Notification
from offers.services import decode_offer, detect_red_flags
from users.models import College, StudentProfile, StudentSkill

User = get_user_model()


class Base(APITestCase):
    def setUp(self):
        self.college = College.objects.create(name="Test College")
        self.company = Company.objects.create(name="TestCo")
        self.py = Skill.objects.create(name="Python", category="language")
        self.sql = Skill.objects.create(name="SQL", category="database")
        self.user = User.objects.create_user("stu", "stu@x.com", "Str0ng!pass#1")
        self.profile = StudentProfile.objects.create(user=self.user, college=self.college, branch="CSE",
                                                     graduation_year=2027, cgpa=Decimal("7.10"), backlogs=0)
        self.drive = PlacementDrive.objects.create(
            company=self.company, college=self.college, title="Software Engineer", status="registration_open",
            drive_date=date.today() + timedelta(days=30), application_deadline=date.today() + timedelta(days=10),
            min_cgpa=Decimal("7.5"), max_backlogs=0, eligible_branches="CSE, IT", graduation_year=2027,
            ctc_total=600000, bond_years=2)
        self.drive.required_skills.set([self.py, self.sql])

    def auth(self, user=None):
        resp = self.client.post("/api/auth/login/", {"username": (user or self.user).username, "password": "Str0ng!pass#1"})
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + resp.data["access"])


class EligibilityTests(Base):
    def test_cgpa_reason_is_explained(self):
        r = check_eligibility(self.profile, self.drive)
        self.assertFalse(r["eligible"])
        self.assertIn("minimum CGPA is 7.5 and your CGPA is 7.1", r["reasons"][0])

    def test_eligible_when_all_pass(self):
        self.profile.cgpa = Decimal("8.0")
        self.profile.save()
        self.assertTrue(check_eligibility(self.profile, self.drive)["eligible"])

    def test_missing_cgpa_is_not_assumed_eligible(self):
        self.profile.cgpa = None
        self.profile.save()
        r = check_eligibility(self.profile, self.drive)
        self.assertFalse(r["eligible"])
        self.assertIn("Cannot verify", r["reasons"][0])

    def test_skill_gaps_listed(self):
        StudentSkill.objects.create(student=self.profile, skill=self.py, level=3)
        self.assertEqual(check_eligibility(self.profile, self.drive)["skill_gaps"], ["SQL"])


class ScoringTests(Base):
    def test_score_has_factors_disclaimer_and_bounds(self):
        m = compute_match(self.profile, self.drive)
        self.assertTrue(0 <= m["match_score"] <= 100)
        self.assertIn("NOT a prediction", m["disclaimer"])
        keys = {f["key"] for f in m["factors"]}
        self.assertEqual(keys, {"eligibility", "skills", "role", "location", "readiness"})

    def test_unscorable_factors_are_excluded_not_zeroed(self):
        m = compute_match(self.profile, self.drive)
        role = next(f for f in m["factors"] if f["key"] == "role")
        self.assertIsNone(role["score"])
        self.assertEqual(role["weight"], 0)


class OfferTests(Base):
    def test_no_invented_components(self):
        d = decode_offer(600000)
        self.assertEqual(d["components"], [])

    def test_estimate_is_labelled(self):
        d = decode_offer(600000, assumed_variable_percent=20)
        self.assertTrue(all(c["kind"] == "estimate" for c in d["components"]))

    def test_bond_flag_and_unspecified(self):
        f = detect_red_flags(self.drive)
        self.assertTrue(any("bond" in x["title"].lower() for x in f["flags"]))
        self.assertIn("Notice period", f["not_specified"])

    def test_inr_format(self):
        self.assertEqual(format_inr(600000), "₹6,00,000")
        self.assertEqual(format_inr(1234567), "₹12,34,567")


class ApiTests(Base):
    def test_register_login_profile_flow(self):
        r = self.client.post("/api/auth/register/", {"username": "new1", "email": "n@x.com", "password": "Str0ng!pass#1", "role": "admin"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(User.objects.get(username="new1").role, "student")  # role cannot be self-assigned
        self.auth(User.objects.get(username="new1"))
        self.assertEqual(self.client.patch("/api/students/profile/", {"cgpa": "7.5", "branch": "CSE"}, format="json").status_code, 200)
        self.assertEqual(self.client.patch("/api/students/profile/", {"cgpa": "11"}, format="json").status_code, 400)

    def test_auth_required(self):
        self.assertEqual(self.client.get("/api/drives/").status_code, 401)

    def test_students_cannot_write_companies(self):
        self.auth()
        self.assertEqual(self.client.post("/api/companies/", {"name": "X"}).status_code, 403)

    def test_eligibility_and_match_endpoints(self):
        self.auth()
        r = self.client.get(f"/api/eligibility/{self.drive.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["verdict"], "Not Eligible")
        self.assertEqual(self.client.get(f"/api/matching/{self.drive.id}/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/drives/{self.drive.id}/difficulty/").status_code, 200)
        self.assertEqual(self.client.get("/api/students/dashboard/").status_code, 200)
        self.assertEqual(self.client.get("/api/recommendations/").status_code, 200)

    def test_cannot_apply_when_not_eligible(self):
        self.auth()
        self.assertEqual(self.client.post(f"/api/drives/{self.drive.id}/apply/").status_code, 400)
        self.profile.cgpa = Decimal("8.0")
        self.profile.save()
        self.assertEqual(self.client.post(f"/api/drives/{self.drive.id}/apply/").status_code, 201)

    def test_roadmap_generate_and_toggle_task(self):
        self.auth()
        r = self.client.post(f"/api/preparation/roadmap/{self.drive.id}/")
        self.assertEqual(r.status_code, 201)
        tid = r.data["tasks"][0]["id"]
        self.assertEqual(self.client.patch(f"/api/preparation/tasks/{tid}/", {"is_done": True}, format="json").status_code, 200)

    def test_compare_has_no_winner(self):
        self.auth()
        d2 = PlacementDrive.objects.create(company=self.company, college=self.college, title="Analyst")
        r = self.client.get(f"/api/matching/compare/?drives={self.drive.id},{d2.id}")
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("best", str(r.data).lower().replace("best-", ""))

    def test_experience_moderation(self):
        self.auth()
        r = self.client.post("/api/experiences/", {"company": self.company.id, "year": 2025, "difficulty": 3,
                             "rounds_count": 3, "summary": "Aptitude then coding then interview, fairly standard.",
                             "questions": [{"round_name": "Coding", "text": "Reverse a string", "topic": "Strings"}]}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["status"], "pending")
        exp_id = r.data["id"]
        other = User.objects.create_user("other", "o@x.com", "Str0ng!pass#1")
        StudentProfile.objects.create(user=other)
        self.auth(other)
        self.assertEqual(self.client.get("/api/experiences/").data["count"], 0)       # pending hidden from others
        self.assertEqual(self.client.post(f"/api/experiences/{exp_id}/moderate/", {"action": "approve"}).status_code, 403)
        admin = User.objects.create_user("adm", "a@x.com", "Str0ng!pass#1", role="admin")
        self.auth(admin)
        self.assertEqual(self.client.post(f"/api/experiences/{exp_id}/moderate/", {"action": "approve"}).status_code, 200)
        self.auth(other)
        self.assertEqual(self.client.get("/api/experiences/").data["count"], 1)
        self.assertTrue(Notification.objects.filter(user=self.user, kind="experience").exists())

    def test_new_drive_notifies_only_eligible(self):
        self.profile.cgpa = Decimal("9.0")
        self.profile.save()
        PlacementDrive.objects.create(company=self.company, college=self.college, title="New Role",
                                      status="upcoming", min_cgpa=Decimal("8.0"))
        self.assertTrue(Notification.objects.filter(user=self.user, kind="new_drive").exists())
