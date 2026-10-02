from django.contrib import admin

from .models import Application, DriveRound, PlacementDrive


class RoundInline(admin.TabularInline):
    model = DriveRound
    extra = 1


@admin.register(PlacementDrive)
class DriveAdmin(admin.ModelAdmin):
    list_display = ("company", "title", "college", "drive_date", "status")
    list_filter = ("status", "college")
    inlines = [RoundInline]
    filter_horizontal = ("required_skills",)


admin.site.register(Application)
