"""
apps/projects/views.py
---------------------------------------------------------------
frontend को assets/js मा भविष्यमा jsonको रूपमा tान्ने endpoint।
शेप roadmap.js/news.js कै mock-data pattern सँग मिल्दो राखिएको छ।
---------------------------------------------------------------
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from . import selectors


def _serialize_project(project, *, include_details: bool = True):
    """include_details=False हुँदा गृहपृष्ठ (Featured) जस्ता ठाउँका लागि केवल
    कार्डमा देखिने न्यूनतम जानकारी मात्र पठाइन्छ — पूर्ण विवरण होइन।"""
    data = {
        "id": project.id,
        "slug": project.slug,
        "title": project.title,
        "summary": project.summary,
        "category": project.category,
        "category_label": project.get_category_display(),
        "status": project.status,
        "status_label": project.get_status_display(),
        "icon_emoji": project.icon_emoji,
        "screenshot_url": project.screenshot_url,
        "is_featured": project.is_featured,
        "updated": project.updated_at.date().isoformat(),
    }
    if not include_details:
        return data

    data.update(
        {
            "description": project.description,
            "introduction": project.introduction,
            "objective": project.objective,
            "key_features": project.key_features_list,
            "target_audience": project.target_audience,
            "priority": project.priority,
            "priority_label": project.get_priority_display(),
            "progress": project.progress,
            "tags": [tag.name for tag in project.tags.all()],
            "action": {
                "available": project.is_downloadable,
                "kind": project.action_kind,
                "label": project.action_label,
                "url": project.download_url if project.is_downloadable else "",
            },
            "release": {
                "version": project.release_version,
                "date": project.release_date.isoformat() if project.release_date else None,
                "notes": project.release_notes,
            },
            "milestones": [
                {
                    "title": m.title,
                    "status": m.status,
                    "status_label": m.get_status_display(),
                    "due_date": m.due_date.isoformat() if m.due_date else None,
                }
                for m in project.milestones.all()
            ],
            "created": project.created_at.date().isoformat(),
        }
    )
    return data


@require_http_methods(["GET"])
def project_list_view(request):
    category = request.GET.get("category")
    status = request.GET.get("status")
    projects = selectors.get_all_projects(category=category, status=status)
    return JsonResponse({"results": [_serialize_project(p) for p in projects]})


@require_http_methods(["GET"])
def featured_project_list_view(request):
    """गृहपृष्ठका लागि — कार्ड मात्र देखिने भएकाले न्यूनतम फिल्ड मात्र पठाउने।"""
    projects = selectors.get_featured_projects()
    return JsonResponse({"results": [_serialize_project(p, include_details=False) for p in projects]})


@require_http_methods(["GET"])
def project_detail_view(request, slug):
    project = selectors.get_project_by_slug(slug)
    if project is None:
        return JsonResponse({"error": "परियोजना फेला परेन।"}, status=404)
    return JsonResponse(_serialize_project(project))
