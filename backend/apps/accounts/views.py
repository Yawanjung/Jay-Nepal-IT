import json

from django.conf import settings
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from . import selectors, services
from .decorators import check_permission
from .services import EmailNotVerifiedError

def _parse_json(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}

@ensure_csrf_cookie
@require_http_methods(["GET"])
def csrf_view(request):
    return JsonResponse({"ok": True, "csrfToken": get_token(request)})

@ratelimit(key='ip', rate=settings.SIGNUP_RATE_LIMIT, block=True)
@require_http_methods(["POST"])
@csrf_protect
def signup_view(request):
    data = _parse_json(request)
    full_name = data.get("fullname", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not full_name or not email or not password:
        return JsonResponse({"ok": False, "error": "सबै फिल्ड आवश्यक छन्।"}, status=400)

    try:
        user = services.register_user(full_name=full_name, email=email, password=password)
    except ValidationError as exc:
        # नोट: validate_password() ले धेरै validator फेल भएमा एकभन्दा बढी
        # सन्देश दिन सक्छ — त्यस्तो बेला .message (singular) ले AttributeError
        # दिन्छ, त्यसैले सधैँ .messages (plural, list) प्रयोग गर्ने।
        return JsonResponse({"ok": False, "error": " ".join(exc.messages)}, status=400)

    return JsonResponse(
        {"ok": True, "user": {"id": user.id, "username": user.username, "email": user.email}}
    )

@ratelimit(key='ip', rate=settings.LOGIN_RATE_LIMIT, block=True)
@require_http_methods(["POST"])
@csrf_protect
def login_view(request):
    data = _parse_json(request)
    identifier = data.get("identifier", "").strip()
    password = data.get("password", "")

    if not identifier or not password:
        return JsonResponse({"ok": False, "error": "इमेल/युजरनेम र पासवर्ड आवश्यक छ।"}, status=400)

    ip_address = request.META.get("REMOTE_ADDR")
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    try:
        user = services.authenticate_login(
            identifier=identifier, password=password, ip_address=ip_address, user_agent=user_agent
        )
    except PermissionDenied as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=429)
    except EmailNotVerifiedError:
        return JsonResponse(
            {
                "ok": False,
                "error": "कृपया पहिले आफ्नो इमेल प्रमाणित गर्नुहोस्। इनबक्स जाँच्नुहोस् वा प्रमाणीकरण इमेल फेरि पठाउनुहोस्।",
                "error_code": "email_not_verified",
            },
            status=403,
        )

    if user is None:
        return JsonResponse({"ok": False, "error": "प्रमाणीकरण असफल भयो।"}, status=401)

    # Session Fixation सुरक्षा
    request.session.cycle_key()
    django_login(request, user)
    return JsonResponse({"ok": True, "user": {"id": user.id, "username": user.username, "role": user.role}})

@require_http_methods(["POST"])
@csrf_protect
def logout_view(request):
    django_logout(request)
    return JsonResponse({"ok": True})

@require_http_methods(["GET"])
def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "लगइन गरिएको छैन।"}, status=401)

    profile = selectors.get_user_profile(request.user)
    return JsonResponse(
        {
            "ok": True,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "role": request.user.role,
                "organization": profile.organization if profile else "",
            },
        }
    )


@require_http_methods(["GET"])
def verify_email_view(request):
    token = request.GET.get("token", "")
    if not token:
        return JsonResponse({"ok": False, "error": "टोकन आवश्यक छ।"}, status=400)

    try:
        user = services.verify_email_token(token=token)
    except ValidationError as exc:
        return JsonResponse({"ok": False, "error": str(exc.message)}, status=400)

    return JsonResponse({"ok": True, "message": "इमेल सफलतापूर्वक प्रमाणित भयो।", "email": user.email})


@require_http_methods(["POST"])
def resend_verification_view(request):
    data = _parse_json(request)
    email = data.get("email", "").strip()
    if not email:
        return JsonResponse({"ok": False, "error": "इमेल आवश्यक छ।"}, status=400)

    services.resend_verification_email(email=email)
    # User enumeration रोक्न, खाता भेटियोस् वा नभेटियोस् उस्तै सन्देश दिने
    return JsonResponse(
        {"ok": True, "message": "यदि यो खाता अवस्थित छ र अझै प्रमाणित छैन भने, प्रमाणीकरण इमेल पठाइयो।"}
    )
