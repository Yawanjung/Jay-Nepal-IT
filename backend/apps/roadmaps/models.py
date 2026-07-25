"""
apps/roadmaps/models.py
---------------------------------------------------------------
Roadmaps: आगामी फिचर पाइपलाइन र रिलिज ट्र्याकरहरू।

नोट: Status choices का values (planned/progress/testing/active)
frontend को assets/js/roadmap.js भित्रको STATUS_META object सँग
जानाजान उस्तै राखिएको छ, ताकि API जोड्दा JS मा परिवर्तन नचाहियोस्।
---------------------------------------------------------------
"""
from django.conf import settings
from django.db import models

from apps.projects.models import Project, Tag


class RoadmapItem(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "योजनामा"
        PROGRESS = "progress", "विकासमा"
        TESTING = "testing", "परीक्षणमा"
        ACTIVE = "active", "सक्रिय"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Tag, on_delete=models.SET_NULL, null=True, blank=True, related_name="roadmap_items"
    )
    related_project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="roadmap_items"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED, db_index=True)
    target_release_date = models.DateField(null=True, blank=True)
    order = models.PositiveSmallIntegerField(
        default=0, help_text="ठाडो रोडम्याप-स्पाइनमा देखिने क्रम (सानो नम्बर माथि देखिन्छ)।"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="roadmap_items"
    )
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = "रोडम्याप वस्तु"
        verbose_name_plural = "रोडम्याप वस्तुहरू"
        ordering = ["order", "-updated_at"]
        indexes = [
            models.Index(fields=["status", "order"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ReleaseTracker(models.Model):
    """रिलिज ट्र्याकर — कुन संस्करणमा कुन-कुन रोडम्याप वस्तु सामेल भयो।"""

    version = models.CharField(max_length=30, unique=True, help_text="जस्तै: v1.2.0")
    release_date = models.DateField()
    changelog = models.TextField(blank=True)
    roadmap_items = models.ManyToManyField(RoadmapItem, related_name="releases", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "रिलिज ट्र्याकर"
        verbose_name_plural = "रिलिज ट्र्याकरहरू"
        ordering = ["-release_date"]

    def __str__(self):
        return f"{self.version} — {self.release_date}"
