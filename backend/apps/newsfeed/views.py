"""
apps/newsfeed/views.py
---------------------------------------------------------------
Response shape frontend को assets/js/news.js को FETCH_NEWS_DATA()
मा भएको mock array सँग मिल्ने गरी design गरिएको छ।
---------------------------------------------------------------
"""
import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from . import selectors, services


def _author_display_name(author):
    """author FK खाली (SET_NULL) हुन सक्ने भएकोले सुरक्षित रूपमा पूरा नाम/username फर्काउने।"""
    if not author:
        return None
    full_name = author.get_full_name()
    return full_name or author.username


def _serialize_news(post):
    return {
        "id": post.id,
        "slug": post.slug,
        "category": post.category,
        "category_label": post.get_category_display(),
        "title": post.title,
        "excerpt": post.excerpt,
        "body": post.body,
        "version": post.version_label or None,
        "author_name": _author_display_name(post.author),
        "published": post.published_at.date().isoformat(),
    }


@require_http_methods(["GET"])
def news_list_view(request):
    category = request.GET.get("category", "all")
    posts = selectors.get_published_news(category=category)
    return JsonResponse({"results": [_serialize_news(p) for p in posts]})


@require_http_methods(["GET"])
def news_detail_view(request, slug):
    post = selectors.get_news_by_slug(slug)
    if post is None:
        return JsonResponse({"error": "समाचार फेला परेन।"}, status=404)

    data = _serialize_news(post)
    data["updated"] = post.updated_at.date().isoformat()
    data["revisions"] = [
        {"revision_number": r.revision_number, "created_at": r.created_at.isoformat()}
        for r in selectors.get_revision_history(post)
    ]
    return JsonResponse(data)


@require_http_methods(["POST"])
def subscribe_view(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        data = {}

    email = data.get("email", "").strip()
    if not email:
        return JsonResponse({"ok": False, "error": "इमेल आवश्यक छ।"}, status=400)

    try:
        services.subscribe_email(email=email)
    except ValidationError as exc:
        return JsonResponse({"ok": False, "error": str(exc.message)}, status=400)

    return JsonResponse({"ok": True})
