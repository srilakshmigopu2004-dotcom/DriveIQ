from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("", views.ExperienceViewSet, basename="experiences")
urlpatterns = router.urls
