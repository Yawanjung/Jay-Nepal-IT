"""
config/urls.py
मुख्य URL राउटर — हरेक app ले आफ्नै urls.py मार्फत /api/ मुनि endpoint expose गर्छ।
"""
from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

admin.site.site_header = "Jay Nepal IT प्रविधि — प्रशासक प्यानल"
admin.site.site_title = "Jay Nepal IT Admin"
admin.site.index_title = "व्यवस्थापन ड्यासबोर्ड"


def healthcheck_view(request):
    """Railway (वा अरू host) को healthcheck probe ले सामान्यतया '/' मा GET पठाउँछ।
    यो URL पहिले परिभाषित नभएकोले 404 फर्किन्थ्यो, र Railway ले त्यसलाई
    "unhealthy" ठानेर container तुरुन्तै बन्द गर्थ्यो — गुनिकर्न सफलतापूर्वक
    बुट भइसके पनि। यो view ले DB/auth केही नछोई तुरुन्तै 200 फर्काउँछ।"""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", healthcheck_view, name="healthcheck"),
    path("health/", healthcheck_view, name="healthcheck-alt"),
    path(settings.ADMIN_URL_PATH, admin.site.urls),

    path("api/accounts/", include("apps.accounts.urls")),
    path("api/projects/", include("apps.projects.urls")),
    path("api/news/", include("apps.newsfeed.urls")),
    path("api/roadmap/", include("apps.roadmaps.urls")),
    path("api/services/", include("apps.services.urls")),
    path("api/team/", include("apps.team.urls")),
]
