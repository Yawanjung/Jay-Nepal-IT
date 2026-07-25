from django.contrib import admin

from .models import ReleaseTracker, RoadmapItem


@admin.register(RoadmapItem)
class RoadmapItemAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "category", "related_project", "target_release_date", "order", "updated_at")
    list_filter = ("status", "category")
    search_fields = ("title", "description")
    ordering = ("order",)


@admin.register(ReleaseTracker)
class ReleaseTrackerAdmin(admin.ModelAdmin):
    list_display = ("version", "release_date", "created_at")
    filter_horizontal = ("roadmap_items",)
    search_fields = ("version",)
