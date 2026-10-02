from django.urls import path

from . import views

urlpatterns = [
    path("compare/", views.CompareView.as_view()),
    path("<int:drive_id>/", views.MatchView.as_view()),
]
