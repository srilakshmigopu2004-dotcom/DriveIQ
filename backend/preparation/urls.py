from django.urls import path

from . import views

urlpatterns = [
    path("readiness/", views.ReadinessView.as_view()),
    path("roadmap/<int:drive_id>/", views.RoadmapView.as_view()),
    path("tasks/<int:pk>/", views.TaskUpdateView.as_view()),
]
