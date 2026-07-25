"""
apps/accounts/models.py
---------------------------------------------------------------
Users: युजर रोल, एक्सेस कन्ट्रोल लिस्ट (ACL), प्रोफाइल, र
अथेन्टिकेशन प्रोटोकलहरू।
---------------------------------------------------------------
"""
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """
    कस्टम प्रयोगकर्ता मोडेल — Django को AbstractUser विस्तार गरेर
    role-based access का लागि आधार तयार पारिएको छ।
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "प्रशासक"
        EDITOR = "editor", "सम्पादक"
        CONTRIBUTOR = "contributor", "योगदानकर्ता"
        VIEWER = "viewer", "दर्शक"

    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        db_index=True,
        help_text="प्रयोगकर्ताको प्रणाली-व्यापी भूमिका (system-wide role)।",
    )
    phone_regex = RegexValidator(
        regex=r"^\+?977?\d{7,10}$",
        message="फोन नम्बर मान्य ढाँचामा हुनुपर्छ, जस्तै: +9779812345678",
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=15, blank=True
    )
    is_two_factor_enabled = models.BooleanField(
        default=False, help_text="दुई-चरण प्रमाणीकरण (2FA) सक्रिय छ/छैन।"
    )
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "प्रयोगकर्ता"
        verbose_name_plural = "प्रयोगकर्ताहरू"
        indexes = [
            models.Index(fields=["role", "is_active"]),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class Profile(models.Model):
    """User सँग एक-एक (OneToOne) सम्बन्ध — विस्तृत प्रोफाइल जानकारी।"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(blank=True, max_length=500)
    organization = models.CharField(max_length=150, blank=True)
    district = models.CharField(
        max_length=100, blank=True, help_text="जिल्ला (जस्तै: भक्तपुर, काठमाडौं)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "प्रोफाइल"
        verbose_name_plural = "प्रोफाइलहरू"

    def __str__(self):
        return f"{self.user.username} को प्रोफाइल"


class AccessControlEntry(models.Model):
    """
    एक्सेस कन्ट्रोल लिस्ट (ACL) — Django को डिफल्ट Group/Permission भन्दा
    थप ग्रानुलर (resource-level) पहुँच व्यवस्थापनका लागि।
    """

    class ResourceType(models.TextChoices):
        PROJECT = "project", "परियोजना"
        NEWS = "news", "समाचार"
        ROADMAP = "roadmap", "रोडम्याप"
        USER = "user", "प्रयोगकर्ता"

    class PermissionLevel(models.TextChoices):
        VIEW = "view", "हेर्न मात्र"
        EDIT = "edit", "सम्पादन"
        MANAGE = "manage", "व्यवस्थापन"
        OWNER = "owner", "स्वामी"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="acl_entries"
    )
    resource_type = models.CharField(
        max_length=20, choices=ResourceType.choices, db_index=True
    )
    resource_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="खाली छोड्नुहोस् यदि यो अनुमति यस resource_type का सबै वस्तुमा लागू हुन्छ भने।",
    )
    permission_level = models.CharField(
        max_length=20, choices=PermissionLevel.choices, default=PermissionLevel.VIEW
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_acl_entries",
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ACL प्रविष्टि"
        verbose_name_plural = "ACL प्रविष्टिहरू"
        unique_together = ("user", "resource_type", "resource_id", "permission_level")
        indexes = [
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def __str__(self):
        target = self.resource_id or "सबै"
        return f"{self.user.username} → {self.get_resource_type_display()}#{target} ({self.get_permission_level_display()})"


class EmailVerificationToken(models.Model):
    """
    इमेल प्रमाणीकरण टोकन — signup पछि प्रयोगकर्ताको इमेल साँच्चै
    उसैको हो भनी पुष्टि गर्न पठाइने एकपटके लिङ्कको आधार।
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_verification_tokens"
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "इमेल प्रमाणीकरण टोकन"
        verbose_name_plural = "इमेल प्रमाणीकरण टोकनहरू"
        ordering = ["-created_at"]

    def is_valid(self):
        from django.utils import timezone

        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.user.username} — {'प्रयोग भयो' if self.is_used else 'बाँकी'}"


class AuthEventLog(models.Model):
    """अथेन्टिकेशन प्रोटोकल लग — लगइन/लगआउट/2FA घटनाहरूको अडिट ट्रेल।"""

    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "सफल लगइन"
        LOGIN_FAILED = "login_failed", "असफल लगइन प्रयास"
        LOGOUT = "logout", "लगआउट"
        PASSWORD_RESET = "password_reset", "पासवर्ड रिसेट"
        TWO_FACTOR_VERIFIED = "two_factor_verified", "2FA प्रमाणित"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="auth_events", null=True, blank=True
    )
    event_type = models.CharField(max_length=30, choices=EventType.choices, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "अथेन्टिकेशन घटना लग"
        verbose_name_plural = "अथेन्टिकेशन घटना लगहरू"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        who = self.user.username if self.user else "अज्ञात"
        return f"{who} — {self.get_event_type_display()} ({self.created_at:%Y-%m-%d %H:%M})"
