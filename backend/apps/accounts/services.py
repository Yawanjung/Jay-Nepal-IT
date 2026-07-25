"""
apps/accounts/services.py
---------------------------------------------------------------
Services = business logic + लेखन (write) कार्यहरू। Views ले सीधै
मोडेल नछोई यहाँका functions मार्फत मात्र डेटा परिवर्तन गर्छन्।
---------------------------------------------------------------
"""
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from . import selectors
from .models import AccessControlEntry, AuthEventLog, EmailVerificationToken, Profile

User = get_user_model()


class EmailNotVerifiedError(Exception):
    """लगइन प्रयास गर्दा इमेल अझै प्रमाणित नभएको अवस्थामा उठाइने त्रुटि।"""

    def __init__(self, user):
        self.user = user
        super().__init__("इमेल अझै प्रमाणित भएको छैन।")


TOKEN_VALIDITY_HOURS = 24


@transaction.atomic
def register_user(*, full_name: str, email: str, password: str) -> User:
    """नयाँ प्रयोगकर्ता खाता बनाउने — signup.html फारमसँग मिल्दो।

    सुरक्षा नोट: फ्रन्टइन्डमा पासवर्डको लम्बाइ मात्र जाँचिन्छ (client-side,
    bypass गर्न सकिने)। settings.py मा तोकिएको AUTH_PASSWORD_VALIDATORS
    (न्यूनतम लम्बाइ, सामान्य/numeric पासवर्ड रोक्ने, आदि) यहाँ
    validate_password() मार्फत server-side मै लागू गरिन्छ — यसले सिधै
    API कल गरेर कमजोर पासवर्ड राख्न खोज्ने प्रयासलाई रोक्छ।
    """
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError("यो इमेलबाट पहिल्यै खाता बनिसकेको छ।")

    username = email.split("@")[0]
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    name_parts = full_name.strip().split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    # पासवर्ड कमजोर भए ValidationError (धेरै साना/सामान्य/numeric-मात्र
    # message हरूसहित) उठ्छ — यो signup_view मा पहिल्यै पक्रिइन्छ।
    validate_password(
        password,
        user=User(username=username, email=email, first_name=first_name, last_name=last_name),
    )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=User.Role.VIEWER,
    )
    Profile.objects.create(user=user)

    token = create_verification_token(user=user)
    send_verification_email(user=user, token=token.token)

    return user


def create_verification_token(*, user) -> EmailVerificationToken:
    token = secrets.token_urlsafe(32)
    return EmailVerificationToken.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(hours=TOKEN_VALIDITY_HOURS),
    )


def send_verification_email(*, user, token: str):
    verify_link = f"{settings.FRONTEND_URL}/verify-email.html?token={token}"
    subject = "Jay Nepal IT प्रविधि — आफ्नो इमेल प्रमाणित गर्नुहोस्"
    message = (
        f"नमस्ते {user.first_name or user.username},\n\n"
        f"Jay Nepal IT प्रविधिमा खाता बनाउनुभएकोमा धन्यवाद।\n"
        f"कृपया तलको लिङ्कमा क्लिक गरेर आफ्नो इमेल प्रमाणित गर्नुहोस्:\n\n"
        f"{verify_link}\n\n"
        f"यो लिङ्क {TOKEN_VALIDITY_HOURS} घण्टासम्म मात्र मान्य हुन्छ।\n"
        f"यदि तपाईंले यो खाता बनाउनुभएको होइन भने, यो इमेल बेवास्ता गर्नुहोस्।"
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def verify_email_token(*, token: str) -> User:
    """टोकन प्रमाणित गरेर user.is_email_verified = True बनाउने।"""
    entry = EmailVerificationToken.objects.filter(token=token).select_related("user").first()

    if entry is None:
        raise ValidationError("अमान्य प्रमाणीकरण लिङ्क।")
    if not entry.is_valid():
        raise ValidationError("यो लिङ्कको म्याद सकिएको छ। कृपया नयाँ लिङ्क माग्नुहोस्।")

    with transaction.atomic():
        entry.is_used = True
        entry.save(update_fields=["is_used"])
        entry.user.is_email_verified = True
        entry.user.save(update_fields=["is_email_verified"])

    return entry.user


def resend_verification_email(*, email: str):
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        # प्रयोगकर्ता खोजी (user enumeration) रोक्न, नभेटिए पनि उस्तै जवाफ दिने
        return
    if user.is_email_verified:
        return

    token = create_verification_token(user=user)
    send_verification_email(user=user, token=token.token)


def authenticate_login(*, identifier: str, password: str, ip_address: str = None, user_agent: str = ""):
    """
    इमेल वा युजरनेम + पासवर्ड प्रयोग गरी लगइन प्रयास गर्ने।
    सफल/असफल दुबै अवस्थामा AuthEventLog मा रेकर्ड राखिन्छ।

    ब्रुट-फोर्स सुरक्षा: एउटै IP बाट १५ मिनेटभित्र ५ भन्दा बढी
    असफल प्रयास भएमा थप प्रयास अस्थायी रूपमा रोकिन्छ।
    """
    if ip_address:
        recent_window = timezone.now() - timedelta(minutes=15)
        recent_failures = AuthEventLog.objects.filter(
            ip_address=ip_address,
            event_type=AuthEventLog.EventType.LOGIN_FAILED,
            created_at__gte=recent_window,
        ).count()
        if recent_failures >= 5:
            raise PermissionDenied(
                "धेरै असफल प्रयासका कारण अस्थायी रूपमा रोकिएको छ। १५ मिनेटपछि फेरि प्रयास गर्नुहोस्।"
            )

    user = selectors.get_user_by_identifier(identifier)
    username = user.username if user else identifier

    authenticated_user = authenticate(username=username, password=password)

    if authenticated_user is None:
        AuthEventLog.objects.create(
            user=user,
            event_type=AuthEventLog.EventType.LOGIN_FAILED,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return None

    if not authenticated_user.is_email_verified:
        raise EmailNotVerifiedError(authenticated_user)

    AuthEventLog.objects.create(
        user=authenticated_user,
        event_type=AuthEventLog.EventType.LOGIN_SUCCESS,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return authenticated_user


@transaction.atomic
def grant_acl_entry(*, user, resource_type: str, resource_id: int | None, permission_level: str, granted_by):
    """कुनै resource माथि अनुमति प्रदान गर्ने (create-or-update)।"""
    entry, _created = AccessControlEntry.objects.update_or_create(
        user=user,
        resource_type=resource_type,
        resource_id=resource_id,
        permission_level=permission_level,
        defaults={"granted_by": granted_by},
    )
    return entry


def update_profile(*, user, **fields):
    profile, _ = Profile.objects.get_or_create(user=user)
    for key, value in fields.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    profile.save()
    return profile
