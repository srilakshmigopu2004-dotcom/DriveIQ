from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("rounds", views.RoundViewSet, basename="rounds")
router.register("", views.DriveViewSet, basename="drives")

urlpatterns = [
    path("applications/", views.MyApplicationsView.as_view()),
    path("", include(router.urls)),
]
