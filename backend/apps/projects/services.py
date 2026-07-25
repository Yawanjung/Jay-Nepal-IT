"""
apps/projects/services.py
---------------------------------------------------------------
Write operations। Admin वा भविष्यको dashboard बाट call हुनेछ।
---------------------------------------------------------------
"""
from django.db import transaction

from .models import Milestone, Project, Tag


@transaction.atomic
def create_project(
    *,
    title,
    summary,
    description="",
    category,
    owner=None,
    tag_names=None,
    icon_emoji="",
    introduction="",
    objective="",
    key_features="",
    target_audience="",
):
    project = Project.objects.create(
        title=title,
        summary=summary,
        description=description,
        category=category,
        owner=owner,
        icon_emoji=icon_emoji,
        introduction=introduction,
        objective=objective,
        key_features=key_features,
        target_audience=target_audience,
    )
    if tag_names:
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        project.tags.set(tags)
    return project


def add_milestone(*, project: Project, title, description="", status=Milestone.Status.PLANNED, due_date=None, order=0):
    return Milestone.objects.create(
        project=project,
        title=title,
        description=description,
        status=status,
        due_date=due_date,
        order=order,
    )


def mark_milestone_completed(*, milestone: Milestone):
    from django.utils import timezone

    milestone.status = Milestone.Status.COMPLETED
    milestone.completed_at = timezone.now()
    milestone.save(update_fields=["status", "completed_at"])
    return milestone
