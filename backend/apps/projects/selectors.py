"""
apps/projects/selectors.py
---------------------------------------------------------------
Read-only queries। frontend को projects.html (jn-project-card,
jn-summary-aside) यहींबाट डेटा पाउँछ भविष्यमा।
---------------------------------------------------------------
"""
from django.db import models

from .models import Project


def get_all_projects(*, category: str = None, status: str = None):
    """Projects Page का लागि — सबै परियोजना (कुनै पनि status), वैकल्पिक category/status फिल्टरसहित।"""
    qs = Project.objects.prefetch_related("tags", "milestones").select_related("owner")
    if category:
        qs = qs.filter(category=category)
    if status:
        qs = qs.filter(status=status)
    return qs


def get_featured_projects(limit: int = 4):
    return (
        Project.objects.filter(is_featured=True)
        .prefetch_related("tags")
        .order_by("-updated_at")[:limit]
    )


def get_project_by_slug(slug: str):
    return Project.objects.prefetch_related("tags", "milestones").filter(slug=slug).first()


def get_roadmap_projects(*, status: str = None):
    """Coming Soon/Roadmap पेजका लागि — योजनामा/विकासमा/परीक्षणमा रहेका परियोजना मात्र।
    (छुट्टै Roadmap डाटाबेसको सट्टा यहीं Projects डाटाबेस प्रयोग गरिन्छ।)"""
    qs = (
        Project.objects.filter(
            status__in=[Project.Status.PLANNED, Project.Status.IN_PROGRESS, Project.Status.TESTING]
        )
        .prefetch_related("tags", "milestones")
    )
    if status:
        qs = qs.filter(status=status)

    priority_order = models.Case(
        models.When(priority=Project.Priority.CRITICAL, then=0),
        models.When(priority=Project.Priority.HIGH, then=1),
        models.When(priority=Project.Priority.MEDIUM, then=2),
        models.When(priority=Project.Priority.LOW, then=3),
        default=4,
        output_field=models.IntegerField(),
    )
    return qs.annotate(_priority_order=priority_order).order_by("_priority_order", "-updated_at")
