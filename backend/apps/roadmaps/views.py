"""
apps/roadmaps/views.py
---------------------------------------------------------------
/api/roadmap/ — Coming Soon (अब "Project Roadmap") पेज र गृहपृष्ठको
मिनी-रोडम्याप विजेटका लागि। डाटा apps.projects को Project
डाटाबेसबाटै आउँछ (छुट्टै Roadmap डाटाबेस छैन)।

Response को "status"/"category" key हरू assets/js/roadmap.js
(गृहपृष्ठ विजेट) सँग legacy-compatible राखिएका छन् (planned/
progress/testing/active + पठनयोग्य category label), भने थप
विस्तृत field हरू (progress, priority, milestones, tags,
target_release, category_code) assets/js/coming-soon.js
(पूर्ण Roadmap पेज) ले प्रयोग गर्छ।
---------------------------------------------------------------
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from . import selectors

_LEGACY_STATUS_KEY = {
    "planned": "planned",
    "in_progress": "progress",
    "testing": "testing",
    "active": "active",
}
_REVERSE_STATUS_KEY = {v: k for k, v in _LEGACY_STATUS_KEY.items()}


def _serialize_roadmap_project(project):
    return {
        "id": f"rm-{project.id:03d}",
        "project_id": project.id,
        "slug": project.slug,
        "title": project.title,
        "description": project.description or project.summary,
        "introduction": project.introduction,
        "objective": project.objective,
        "key_features": project.key_features_list,
        "target_audience": project.target_audience,
        "category": project.get_category_display(),
        "category_code": project.category,
        "status": _LEGACY_STATUS_KEY.get(project.status, project.status),
        "status_label": project.get_status_display(),
        "priority": project.priority,
        "priority_label": project.get_priority_display(),
        "progress": project.progress,
        "tags": [tag.name for tag in project.tags.all()],
        "milestones": [
            {
                "title": m.title,
                "status": m.status,
                "status_label": m.get_status_display(),
                "due_date": m.due_date.isoformat() if m.due_date else None,
            }
            for m in project.milestones.all()
        ],
        "action": {
            "available": project.is_downloadable,
            "kind": project.action_kind,
            "label": project.action_label,
            "url": project.download_url if project.is_downloadable else "",
        },
        "target_release": {
            "version": project.release_version,
            "date": project.release_date.isoformat() if project.release_date else None,
        },
        "updated": project.updated_at.date().isoformat(),
    }


@require_http_methods(["GET"])
def roadmap_list_view(request):
    status = request.GET.get("status")
    if status in _REVERSE_STATUS_KEY:
        status = _REVERSE_STATUS_KEY[status]
    items = selectors.get_roadmap_projects(status=status)
    return JsonResponse({"results": [_serialize_roadmap_project(p) for p in items]})
