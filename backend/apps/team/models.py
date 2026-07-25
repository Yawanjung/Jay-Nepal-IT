from django.db import models


class TeamMember(models.Model):
    name = models.CharField(max_length=120, help_text="जस्तै: 'वेब डेभलपर' वा साँचो नाम।")
    role = models.CharField(max_length=150, help_text="जस्तै: फ्रन्टइन्ड तथा पहुँचयोग्यता।")
    bio = models.CharField(max_length=300, blank=True)
    initials = models.CharField(
        max_length=4, blank=True, help_text="Avatar circle मा देखिने छोटो अक्षर, जस्तै 'वे'।"
    )
    avatar_url = models.URLField(blank=True, help_text="फोटो राख्न चाहनुभए URL (वैकल्पिक)।")
    portfolio_url = models.URLField(
        blank=True, help_text="व्यक्तिगत वेबसाइट/पोर्टफोलियो लिङ्क (वैकल्पिक)।"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="सानो नम्बर पहिले देखिन्छ।")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "टोली सदस्य"
        verbose_name_plural = "टोली सदस्यहरू"
        ordering = ["order", "name"]
        indexes = [models.Index(fields=["is_active", "order"])]

    def __str__(self):
        return f"{self.name} — {self.role}"
