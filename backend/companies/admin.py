from django.contrib import admin

from .models import Company, CompanyTechnology, JobRole, SavedCompany, Skill


class TechInline(admin.TabularInline):
    model = CompanyTechnology
    extra = 1


class RoleInline(admin.TabularInline):
    model = JobRole
    extra = 0


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "category", "company_size")
    search_fields = ("name",)
    inlines = [TechInline, RoleInline]


admin.site.register([Skill, JobRole, SavedCompany])
