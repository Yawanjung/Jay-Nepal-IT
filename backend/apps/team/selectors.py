from .models import TeamMember


def get_active_team_members():
    return TeamMember.objects.filter(is_active=True).order_by("order", "name")
