"""
apps/roadmaps/services.py
---------------------------------------------------------------
लेखन (write) कार्यहरू — रोडम्याप वस्तु थप्ने/स्थिति परिवर्तन गर्ने/
रिलिजमा जोड्ने।
---------------------------------------------------------------
"""
from django.db import transaction

from .models import ReleaseTracker, RoadmapItem


def create_roadmap_item(*, title, description="", category=None, related_project=None, status=RoadmapItem.Status.PLANNED, order=0, created_by=None):
    return RoadmapItem.objects.create(
        title=title,
        description=description,
        category=category,
        related_project=related_project,
        status=status,
        order=order,
        created_by=created_by,
    )


def advance_status(*, roadmap_item: RoadmapItem, new_status: str):
    if new_status not in RoadmapItem.Status.values:
        raise ValueError("अमान्य स्थिति।")
    roadmap_item.status = new_status
    roadmap_item.save(update_fields=["status", "updated_at"])
    return roadmap_item


@transaction.atomic
def create_release(*, version, release_date, changelog="", roadmap_item_ids=None):
    release = ReleaseTracker.objects.create(version=version, release_date=release_date, changelog=changelog)
    if roadmap_item_ids:
        items = RoadmapItem.objects.filter(id__in=roadmap_item_ids)
        release.roadmap_items.set(items)
        items.update(status=RoadmapItem.Status.ACTIVE)
    return release
