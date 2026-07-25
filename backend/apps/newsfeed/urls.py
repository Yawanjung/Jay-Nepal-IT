from django.urls import path

from . import views

app_name = "newsfeed"

urlpatterns = [
    path("", views.news_list_view, name="list"),
    path("subscribe/", views.subscribe_view, name="subscribe"),
    path("<slug:slug>/", views.news_detail_view, name="detail"),
]
