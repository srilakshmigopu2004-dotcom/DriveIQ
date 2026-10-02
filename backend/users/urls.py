from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("skills", views.SkillViewSet, basename="my-skills")
router.register("projects", views.ProjectViewSet, basename="my-projects")
router.register("internships", views.InternshipViewSet, basename="my-internships")
router.register("certifications", views.CertificationViewSet, basename="my-certifications")
router.register("colleges", views.CollegeViewSet, basename="colleges")

urlpatterns = [
    path("profile/", views.ProfileView.as_view()),
    path("dashboard/", views.DashboardView.as_view()),
    path("", include(router.urls)),
]
