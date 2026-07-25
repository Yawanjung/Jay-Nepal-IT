"""
apps/accounts/selectors.py
---------------------------------------------------------------
Selectors = केवल पढ्ने (read) queries। यहाँ कुनै पनि डेटा
परिवर्तन (write) गरिँदैन — त्यो services.py को जिम्मेवारी हो।
---------------------------------------------------------------
"""
from django.contrib.auth import get_user_model
from django.db.models import Value
from django.db.models.functions import Concat

from .models import AccessControlEntry

User = get_user_model()


def get_user_by_identifier(identifier: str):
    """इमेल, युजरनेम, वा पूरा नाम (First + Last) — तीनवटैबाट प्रयोगकर्ता खोज्ने।"""
    identifier = identifier.strip()

    user = User.objects.filter(email__iexact=identifier).first()
    if user:
        return user

    user = User.objects.filter(username__iexact=identifier).first()
    if user:
        return user

    user = (
        User.objects.annotate(full_name=Concat("first_name", Value(" "), "last_name"))
        .filter(full_name__iexact=identifier)
        .first()
    )
    return user


def get_user_profile(user):
    return getattr(user, "profile", None)


def get_acl_entries_for_user(user):
    return AccessControlEntry.objects.filter(user=user).select_related("granted_by")


def user_has_permission(user, resource_type: str, resource_id: int | None, min_level: str) -> bool:
    """
    दिइएको user को resource_type/resource_id माथि कम्तीमा min_level
    अनुमति छ कि छैन जाँच्ने। resource_id=None भएको ACL प्रविष्टिले
    त्यो resource_type का सबै वस्तुमा अनुमति दिन्छ।
    """
    if user.is_superuser or user.role == User.Role.ADMIN:
        return True

    level_order = {"view": 1, "edit": 2, "manage": 3, "owner": 4}
    required = level_order.get(min_level, 1)

    entries = AccessControlEntry.objects.filter(
        user=user, resource_type=resource_type
    ).filter(models_q_resource(resource_id))

    return any(level_order.get(e.permission_level, 0) >= required for e in entries)


def models_q_resource(resource_id):
    from django.db.models import Q

    return Q(resource_id=resource_id) | Q(resource_id__isnull=True)


def get_recent_auth_events(user, limit: int = 20):
    return user.auth_events.all()[:limit]
