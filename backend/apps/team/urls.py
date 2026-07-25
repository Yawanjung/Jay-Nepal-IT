from django.urls import path

from . import views

app_name = "team"

urlpatterns = [
    path("", views.team_list_view, name="list"),
]
