"""
apps/services/models.py
---------------------------------------------------------------
Services: कम्पनीले प्रदान गर्ने सेवाहरू (वेबसाइट डिजाइन, एप विकास,
आईटी परामर्श, आदि)। Admin बाट थपेको/हटाएको तुरुन्तै services.html
मा देखिन्छ — hardcoded होइन।
---------------------------------------------------------------
"""
from django.db import models
from django.utils.text import slugify


class Service(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    summary = models.CharField(
        max_length=250, help_text="कार्डमा देखिने छोटो विवरण।"
    )
    description = models.TextField(
        blank=True, help_text="विस्तृत विवरण (भविष्यमा detail page का लागि)।"
    )
    icon_emoji = models.CharField(
        max_length=10, blank=True, help_text="कार्डमा देखाउने इमोजी, जस्तै 🖥️"
    )
    price_note = models.CharField(
        max_length=150,
        blank=True,
        help_text="जस्तै: 'निःशुल्क परामर्श' वा 'मूल्यको लागि सम्पर्क गर्नुहोस्'।",
    )
    is_active = models.BooleanField(
        default=True, db_index=True, help_text="अनचेक गरे यो सेवा वेबसाइटमा देखिँदैन।"
    )
    order = models.PositiveSmallIntegerField(
        default=0, help_text="सानो नम्बर पहिले देखिन्छ।"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "सेवा"
        verbose_name_plural = "सेवाहरू"
        ordering = ["order", "title"]
        indexes = [
            models.Index(fields=["is_active", "order"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
