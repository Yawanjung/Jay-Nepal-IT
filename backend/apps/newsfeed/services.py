"""
apps/newsfeed/services.py
---------------------------------------------------------------
लेखन (write) कार्यहरू। NewsPost.save() ले आफै रिभिजन ब्यवस्थापन
गर्छ, त्यसैले यहाँ मुख्यतया फिल्ड-लेभल validation/orchestration।
---------------------------------------------------------------
"""
import re

from django.core.exceptions import ValidationError

from .models import NewsletterSubscriber, NewsPost

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def subscribe_email(*, email: str) -> NewsletterSubscriber:
    email = email.strip().lower()
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("कृपया मान्य इमेल ठेगाना लेख्नुहोस्।")

    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email, defaults={"is_active": True}
    )
    if not created and not subscriber.is_active:
        subscriber.is_active = True
        subscriber.save(update_fields=["is_active"])
    return subscriber


def publish_news_post(*, title, excerpt, category, body="", version_label="", related_project=None, author=None):
    if category not in NewsPost.Category.values:
        raise ValidationError("अमान्य समाचार श्रेणी।")

    return NewsPost.objects.create(
        title=title,
        excerpt=excerpt,
        body=body,
        category=category,
        version_label=version_label,
        related_project=related_project,
        author=author,
    )


def update_news_post(*, news_post: NewsPost, **fields):
    for key, value in fields.items():
        if hasattr(news_post, key):
            setattr(news_post, key, value)
    news_post.save()  # save() override ले नयाँ रिभिजन थप्नेछ
    return news_post


def unpublish_news_post(*, news_post: NewsPost):
    news_post.is_published = False
    news_post.save(update_fields=["is_published"])
    return news_post
