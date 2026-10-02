from django.db import models


class Skill(models.Model):
    class Category(models.TextChoices):
        LANGUAGE = "language", "Programming language"
        FRAMEWORK = "framework", "Framework / library"
        DATABASE = "database", "Database"
        CONCEPT = "concept", "CS concept"
        TOOL = "tool", "Tool"
        OTHER = "other", "Other"

    name = models.CharField(max_length=80, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Company(models.Model):
    """Company 360 profile. Every field is admin-entered; nothing is hard-coded in the UI."""
    name = models.CharField(max_length=150, unique=True)
    logo_url = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, blank=True, help_text="e.g. Product, Service, Startup")
    products_services = models.TextField(blank=True)
    company_size = models.CharField(max_length=60, blank=True, help_text="Approximate, e.g. 10,000+")
    locations = models.CharField(max_length=300, blank=True, help_text="Comma separated")
    careers_url = models.URLField(blank=True)
    campus_hiring_info = models.TextField(blank=True)
    typical_selection_process = models.TextField(blank=True)
    ctc_information = models.TextField(blank=True)
    important_requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class CompanyTechnology(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="technologies")
    name = models.CharField(max_length=80)

    class Meta:
        unique_together = ("company", "name")
        verbose_name_plural = "company technologies"

    def __str__(self):
        return f"{self.company} - {self.name}"


class JobRole(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="roles")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    required_skills = models.ManyToManyField(Skill, blank=True, related_name="roles")

    class Meta:
        unique_together = ("company", "title")

    def __str__(self):
        return f"{self.title} @ {self.company}"


class SavedCompany(models.Model):
    student = models.ForeignKey("users.StudentProfile", on_delete=models.CASCADE, related_name="saved_companies")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "company")
