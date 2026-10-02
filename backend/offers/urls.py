from django.urls import path

from . import views

urlpatterns = [
    path("decode/", views.DecodeView.as_view()),
    path("drive/<int:drive_id>/", views.DriveOfferView.as_view()),
]
