"""
config/urls.py
मुख्य URL राउटर — हरेक app ले आफ्नै urls.py मार्फत /api/ मुनि endpoint expose गर्छ।
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Jay Nepal IT प्रविधि — प्रशासक प्यानल"
admin.site.site_title = "Jay Nepal IT Admin"
admin.site.index_title = "व्यवस्थापन ड्यासबोर्ड"

urlpatterns = [
    path(settings.ADMIN_URL_PATH, admin.site.urls),

    path("api/accounts/", include("apps.accounts.urls")),
    path("api/projects/", include("apps.projects.urls")),
    path("api/news/", include("apps.newsfeed.urls")),
    path("api/roadmap/", include("apps.roadmaps.urls")),
    path("api/services/", include("apps.services.urls")),
    path("api/team/", include("apps.team.urls")),
]
