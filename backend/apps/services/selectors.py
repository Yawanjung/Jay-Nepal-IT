"""
apps/services/selectors.py
---------------------------------------------------------------
Read-only queries। frontend को services.html यहींबाट data पाउँछ।
---------------------------------------------------------------
"""
from .models import Service


def get_active_services():
    return Service.objects.filter(is_active=True).order_by("order", "title")


def get_service_by_slug(slug: str):
    return Service.objects.filter(slug=slug, is_active=True).first()
