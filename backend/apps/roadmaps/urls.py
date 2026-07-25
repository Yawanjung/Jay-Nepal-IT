from django.urls import path

from . import views

app_name = "roadmaps"

urlpatterns = [
    path("", views.roadmap_list_view, name="list"),
]
