"""
apps/services/services.py
---------------------------------------------------------------
लेखन (write) कार्यहरू। हाल Admin panel बाटै व्यवस्थापन हुन्छ, तर
भविष्यमा dashboard/API बाट थप्न चाहेमा यहीं प्रयोग गर्ने।
---------------------------------------------------------------
"""
from .models import Service


def create_service(*, title, summary, description="", icon_emoji="", price_note="", order=0):
    return Service.objects.create(
        title=title,
        summary=summary,
        description=description,
        icon_emoji=icon_emoji,
        price_note=price_note,
        order=order,
    )


def deactivate_service(*, service: Service):
    service.is_active = False
    service.save(update_fields=["is_active"])
    return service
