from django.contrib import admin

from .models import NewsletterSubscriber, NewsPost, NewsRevision


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active",)
    search_fields = ("email",)


class NewsRevisionInline(admin.TabularInline):
    model = NewsRevision
    extra = 0
    readonly_fields = ("revision_number", "title_snapshot", "body_snapshot", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "version_label", "is_published", "published_at", "updated_at")
    list_filter = ("category", "is_published")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [NewsRevisionInline]
    readonly_fields = ("published_at", "updated_at")
    radio_fields = {} 