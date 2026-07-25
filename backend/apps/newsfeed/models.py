"""
apps/newsfeed/models.py
---------------------------------------------------------------
News Feed: वर्गीकृत समाचारहरू ("विशेष समाचार", "सफ्टवेयर माइलस्टोन",
"समुदाय अपडेटहरू"), भर्सन कन्ट्रोल लग, र अटोमेटेड टाइमस्ट्याम्प।
---------------------------------------------------------------
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.projects.models import Project


class NewsletterSubscriber(models.Model):
    """होमपेज/'शीघ्र आउँदैछ' पेजको सदस्यता फारमबाट आउने इमेलहरू।"""

    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "समाचार सदस्यता"
        verbose_name_plural = "समाचार सदस्यताहरू"
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email


class NewsPost(models.Model):
    """मुख्य समाचार/माइलस्टोन/अपडेट प्रविष्टि।"""

    class Category(models.TextChoices):
        SPECIAL = "special", "विशेष समाचार"
        MILESTONE = "milestone", "सफ्टवेयर माइलस्टोन"
        COMMUNITY = "community", "समुदाय अपडेटहरू"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    excerpt = models.CharField(max_length=300)
    body = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, db_index=True)
    version_label = models.CharField(
        max_length=30,
        blank=True,
        help_text="सफ्टवेयर संस्करण ट्याग, जस्तै: v1.2.0 (माइलस्टोन समाचारका लागि)।",
    )
    related_project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="news_posts"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="news_posts"
    )
    is_published = models.BooleanField(default=True, db_index=True)

    # अटोमेटेड टाइमस्ट्याम्पहरू — auto_now_add/auto_now ले manual entry नचाहिने
    published_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "समाचार"
        verbose_name_plural = "समाचारहरू"
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["category", "is_published", "published_at"]),
        ]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

        if not is_new:
            # प्रत्येक अपडेटमा एउटा नयाँ रिभिजन (भर्सन कन्ट्रोल लग) थपिन्छ।
            latest = self.revisions.order_by("-revision_number").first()
            next_number = (latest.revision_number + 1) if latest else 1
            NewsRevision.objects.create(
                news_post=self,
                revision_number=next_number,
                title_snapshot=self.title,
                body_snapshot=self.body,
            )

    def __str__(self):
        return self.title


class NewsRevision(models.Model):
    """
    भर्सन कन्ट्रोल लग — हरेक पटक NewsPost सम्पादन हुँदा एउटा snapshot
    यहाँ सुरक्षित हुन्छ, ताकि परिवर्तनको इतिहास ट्र्याक गर्न सकियोस्।
    """

    news_post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name="revisions")
    revision_number = models.PositiveIntegerField()
    title_snapshot = models.CharField(max_length=250)
    body_snapshot = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "समाचार रिभिजन"
        verbose_name_plural = "समाचार रिभिजनहरू"
        ordering = ["news_post", "-revision_number"]
        unique_together = ("news_post", "revision_number")

    def __str__(self):
        return f"{self.news_post.title} — रिभिजन #{self.revision_number}"
