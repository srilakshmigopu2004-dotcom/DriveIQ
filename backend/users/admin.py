from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Certification, College, Internship, Project, StudentProfile, StudentSkill, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("email", "role")}),)
    list_display = ("username", "email", "role", "is_staff")


class SkillInline(admin.TabularInline):
    model = StudentSkill
    extra = 0


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "college", "branch", "graduation_year", "cgpa", "backlogs")
    inlines = [SkillInline]


admin.site.register(College)
admin.site.register([Project, Internship, Certification])
