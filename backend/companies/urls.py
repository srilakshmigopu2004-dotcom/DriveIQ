from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("skills", views.SkillViewSet, basename="skills")
router.register("roles", views.JobRoleViewSet, basename="roles")
router.register("", views.CompanyViewSet, basename="companies")

urlpatterns = [path("", include(router.urls))]
