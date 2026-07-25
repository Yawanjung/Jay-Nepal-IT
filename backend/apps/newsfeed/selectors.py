"""
apps/newsfeed/selectors.py
---------------------------------------------------------------
frontend को news.html (jn-filter-btn + jn-news-grid) यहींबाट
category-अनुसार फिल्टर गरिएको समाचार पाउँछ।
---------------------------------------------------------------
"""
from .models import NewsPost


def get_published_news(*, category: str = None):
    qs = NewsPost.objects.filter(is_published=True).select_related("related_project", "author")
    if category and category != "all":
        qs = qs.filter(category=category)
    return qs


def get_news_by_slug(slug: str):
    """सुरक्षा नोट: is_published=True नराखे, अझै publish नभएको/draft समाचार पनि
    सिधै URL मार्फत (slug थाहा पाएमा) सार्वजनिक रूपमा हेर्न सकिने हुन्थ्यो।
    get_published_news() सँग मिल्ने गरी यहाँ पनि प्रकाशित समाचार मात्र फर्काउने।"""
    return (
        NewsPost.objects.filter(is_published=True)
        .prefetch_related("revisions")
        .select_related("related_project", "author")
        .filter(slug=slug)
        .first()
    )


def get_revision_history(news_post):
    return news_post.revisions.order_by("-revision_number")
