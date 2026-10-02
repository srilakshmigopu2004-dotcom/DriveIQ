from django.db import models


class PlacementDrive(models.Model):
    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        REGISTRATION_OPEN = "registration_open", "Registration Open"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE, related_name="drives")
    college = models.ForeignKey("users.College", on_delete=models.CASCADE, related_name="drives")
    job_role = models.ForeignKey("companies.JobRole", null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="drives")
    title = models.CharField(max_length=150, help_text="Role title shown to students")
    description = models.TextField(blank=True)
    drive_date = models.DateField(null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPCOMING)
    location = models.CharField(max_length=120, blank=True)
    openings = models.PositiveIntegerField(null=True, blank=True)

    # Eligibility criteria (null / blank = no restriction)
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    max_backlogs = models.PositiveIntegerField(null=True, blank=True)
    eligible_branches = models.CharField(max_length=300, blank=True, help_text="Comma separated; blank = all")
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    required_skills = models.ManyToManyField("companies.Skill", blank=True, related_name="drives")

    # Offer terms. null = NOT SPECIFIED (never treated as zero). Amounts in INR per year.
    ctc_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    ctc_fixed = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    ctc_variable = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    joining_bonus = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    other_components = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bond_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    bond_penalty = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notice_period_days = models.PositiveIntegerField(null=True, blank=True)
    probation_months = models.PositiveIntegerField(null=True, blank=True)
    relocation_required = models.BooleanField(null=True, blank=True)
    training_agreement = models.BooleanField(null=True, blank=True)
    terms_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["drive_date", "-created_at"]

    def __str__(self):
        return f"{self.company} - {self.title}"


class DriveRound(models.Model):
    class Type(models.TextChoices):
        APTITUDE = "aptitude", "Aptitude"
        CODING = "coding", "Coding"
        TECHNICAL = "technical", "Technical interview"
        HR = "hr", "HR interview"
        GD = "gd", "Group discussion"
        OTHER = "other", "Other"

    drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE, related_name="rounds")
    order = models.PositiveSmallIntegerField(default=1)
    name = models.CharField(max_length=100)
    round_type = models.CharField(max_length=20, choices=Type.choices, default=Type.OTHER)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    difficulty = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1 easy, 2 medium, 3 hard; blank = unknown")

    class Meta:
        ordering = ["drive", "order"]


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"
        SELECTED = "selected", "Selected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    student = models.ForeignKey("users.StudentProfile", on_delete=models.CASCADE, related_name="applications")
    drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "drive")
        ordering = ["-created_at"]
