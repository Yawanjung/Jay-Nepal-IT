from functools import wraps
from django.http import JsonResponse
from .models import AccessControlEntry

def check_permission(resource_type, permission_level):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"ok": False, "error": "तपाईं लगइन हुनुहुन्न।"}, status=401)
            
            # Admin Bypass (एडमिनलाई सबै एक्सेस)
            if request.user.role == 'admin':
                return view_func(request, *args, **kwargs)

            resource_id = kwargs.get('resource_id', None)
            has_permission = AccessControlEntry.objects.filter(
                user=request.user,
                resource_type=resource_type,
                resource_id__in=[resource_id, None],
                permission_level=permission_level
            ).exists()

            if has_permission:
                return view_func(request, *args, **kwargs)
            return JsonResponse({"ok": False, "error": "तपाईंसँग यो कार्य गर्ने अनुमति छैन।"}, status=403)
        return _wrapped_view
    return decorator