from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AccessControlEntry, AuthEventLog, EmailVerificationToken, Profile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_two_factor_enabled", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_two_factor_enabled")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (
        ("भूमिका र सुरक्षा", {"fields": ("role", "phone_number", "is_two_factor_enabled", "is_email_verified")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "district", "updated_at")
    search_fields = ("user__username", "organization", "district")


@admin.register(AccessControlEntry)
class AccessControlEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "resource_type", "resource_id", "permission_level", "granted_by", "granted_at")
    list_filter = ("resource_type", "permission_level")
    search_fields = ("user__username",)


@admin.register(AuthEventLog)
class AuthEventLogAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "ip_address", "created_at")
    list_filter = ("event_type",)
    search_fields = ("user__username", "ip_address")
    readonly_fields = ("created_at",)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "is_used", "created_at", "expires_at")
    list_filter = ("is_used",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("token", "created_at")
