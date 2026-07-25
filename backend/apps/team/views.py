from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from . import selectors


def _serialize_member(member):
    return {
        "id": member.id,
        "name": member.name,
        "role": member.role,
        "bio": member.bio,
        "initials": member.initials or member.name[:2],
        "avatar_url": member.avatar_url,
        "portfolio_url": member.portfolio_url,
    }


@require_http_methods(["GET"])
def team_list_view(request):
    members = selectors.get_active_team_members()
    return JsonResponse({"results": [_serialize_member(m) for m in members]})
