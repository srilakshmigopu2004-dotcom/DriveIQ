from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from matching.views import EligibilityView, RecommendationView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.auth_urls")),
    path("api/students/", include("users.urls")),
    path("api/companies/", include("companies.urls")),
    path("api/drives/", include("drives.urls")),
    path("api/eligibility/<int:drive_id>/", EligibilityView.as_view()),
    path("api/matching/", include("matching.urls")),
    path("api/recommendations/", RecommendationView.as_view()),
    path("api/preparation/", include("preparation.urls")),
    path("api/experiences/", include("experiences.urls")),
    path("api/offers/", include("offers.urls")),
    path("api/notifications/", include("notifications.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
