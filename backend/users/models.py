from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models


class Level(models.IntegerChoices):
    BEGINNER = 1, "Beginner"
    INTERMEDIATE = 2, "Intermediate"
    STRONG = 3, "Strong"


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        ADMIN = "admin", "Placement Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_staff

    def __str__(self):
        return self.username


class College(models.Model):
    name = models.CharField(max_length=200, unique=True)
    city = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=150, blank=True)
    college = models.ForeignKey(College, null=True, blank=True, on_delete=models.SET_NULL, related_name="students")
    degree = models.CharField(max_length=80, blank=True)
    branch = models.CharField(max_length=80, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True,
                                                  validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,
                               validators=[MinValueValidator(0), MaxValueValidator(10)])
    backlogs = models.PositiveIntegerField(default=0)
    dsa_level = models.PositiveSmallIntegerField(choices=Level.choices, default=Level.BEGINNER)
    aptitude_level = models.PositiveSmallIntegerField(choices=Level.choices, default=Level.BEGINNER)
    communication_level = models.PositiveSmallIntegerField(choices=Level.choices, default=Level.BEGINNER)
    preferred_roles = models.CharField(max_length=300, blank=True, help_text="Comma separated")
    preferred_locations = models.CharField(max_length=300, blank=True, help_text="Comma separated")
    resume = models.FileField(upload_to="resumes/", blank=True,
                              validators=[FileExtensionValidator(["pdf", "doc", "docx"])])
    skills = models.ManyToManyField("companies.Skill", through="StudentSkill", related_name="students")
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_complete(self):
        return bool(self.college_id and self.branch and self.graduation_year and self.cgpa is not None)

    def __str__(self):
        return self.full_name or self.user.username


class StudentSkill(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="student_skills")
    skill = models.ForeignKey("companies.Skill", on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(choices=Level.choices, default=Level.BEGINNER)

    class Meta:
        unique_together = ("student", "skill")


class Project(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    technologies = models.CharField(max_length=300, blank=True)


class Internship(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="internships")
    company_name = models.CharField(max_length=150)
    role = models.CharField(max_length=120, blank=True)
    duration_months = models.PositiveSmallIntegerField(default=1)


class Certification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=150)
    issuer = models.CharField(max_length=150, blank=True)
