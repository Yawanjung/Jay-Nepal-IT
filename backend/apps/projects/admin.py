"""
apps/projects/admin.py
---------------------------------------------------------------
Projects/Milestones/Tags को Admin पेज।

Accessibility नोट: Django Admin ले ForeignKey/ManyToMany फिल्डको
छेउमा सानो "थप्नुहोस्/परिवर्तन गर्नुहोस्" (pencil/plus) आइकनहरू
देखाउँछ, जुन स्क्रिन रिडरका लागि प्रायः "Edit" जस्तो अस्पष्ट मात्र
सुनिन्छ (कुन कुरा edit गर्ने भन्ने स्पष्ट हुँदैन)। तलको
formfield_for_foreignkey/formfield_for_manytomany override हरूले
ती अस्पष्ट आइकन बटनहरू हटाई (can_add_related=False आदि), बदलामा
सफा dropdown/चयन-बाकस मात्र देखाउँछ, र प्रत्येकमा स्पष्ट aria-label
थप्छ। साथै हरेक fieldset मा "description" राखिएको छ जसले त्यो
सेक्सनमा के भर्ने भनेर स्क्रिन रिडर/दृष्टिविहीन प्रयोगकर्तालाई
अगाडि नै स्पष्ट पार्छ।
---------------------------------------------------------------
"""
from django.contrib import admin

from .models import Milestone, Project, Tag


def _disable_related_widget_icons(field, aria_label):
    """FK/M2M फिल्डको छेउमा आउने अस्पष्ट Add/Change/Delete/View आइकनहरू हटाउने
    र सट्टामा स्पष्ट aria-label सहितको सफा widget मात्र राख्ने।
    नोट: यो Django ले widget लाई RelatedFieldWidgetWrapper भित्र लपेट्ने काम
    सकिसकेपछि (formfield_for_dbfield मा) मात्र चल्नुपर्छ — formfield_for_foreignkey/
    formfield_for_manytomany मा यो लगाउँदा widget अझै लपेटिएको हुँदैन, त्यसैले
    can_add_related जस्ता attribute हरूमा कुनै असर पर्दैन।"""
    widget = field.widget
    if hasattr(widget, "can_add_related"):
        widget.can_add_related = False
    if hasattr(widget, "can_change_related"):
        widget.can_change_related = False
    if hasattr(widget, "can_delete_related"):
        widget.can_delete_related = False
    if hasattr(widget, "can_view_related"):
        widget.can_view_related = False
    widget.attrs.update({"aria-label": aria_label})
    return field


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1
    verbose_name = "माइलस्टोन"
    verbose_name_plural = "माइलस्टोनहरू — यो परियोजनाका चरणबद्ध कामहरू यहाँ थप्नुहोस्"
    fields = ("title", "description", "status", "due_date", "completed_at", "order")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color_hex")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "priority",
        "progress",
        "is_featured",
        "owner",
        "updated_at",
    )
    list_filter = ("category", "status", "priority", "is_featured", "tags")
    search_fields = ("title", "summary", "description", "introduction")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    inlines = [MilestoneInline]
    fieldsets = (
        (
            "आधारभूत जानकारी",
            {
                "description": (
                    "परियोजनाको नाम, स्लग, छोटो सारांश र (वैकल्पिक) पुरानो विवरण "
                    "यहाँ भर्नुहोस्। छोटो सारांश कार्डमा देखिन्छ।"
                ),
                "fields": ("title", "slug", "summary", "description", "icon_emoji"),
            },
        ),
        (
            "संरचित विवरण (Introduction, Objective, Features, Audience)",
            {
                "description": (
                    "यहाँ ४ वटा छुट्टाछुट्टै फिल्डमा परियोजनाको पूर्ण विवरण भर्नुहोस्: "
                    "'परिचय' मा यो के हो भनेर लेख्नुहोस्, 'उद्देश्य' मा किन बनाइयो भनेर, "
                    "'मुख्य विशेषताहरू' मा हरेक विशेषता छुट्टै लाइनमा, र "
                    "'लक्षित प्रयोगकर्ता समूह' मा यो कसका लागि हो भनेर लेख्नुहोस्।"
                ),
                "fields": ("introduction", "objective", "key_features", "target_audience"),
            },
        ),
        (
            "वर्गीकरण (Category, Status, Priority)",
            {
                "description": (
                    "श्रेणी अनुसार नै तल दिइने Action बटन (Download/Visit Live Site) "
                    "स्वतः तय हुन्छ। अवस्था (Status) र प्राथमिकता (Priority) ले यो "
                    "परियोजना Projects Page र Roadmap Page मा कसरी देखिन्छ भन्ने "
                    "निर्धारण गर्छ।"
                ),
                "fields": ("category", "tags", "status", "priority", "progress", "is_featured", "owner"),
            },
        ),
        (
            "रिलिज जानकारी (Release Information)",
            {
                "description": (
                    "Testing वा Active अवस्थामा पुगेपछि यहाँको लिङ्कबाटै Download "
                    "(सफ्टवेयर/मोबाइल एप/गेम) वा Visit Live Site (वेब पोर्टल) बटन "
                    "देखिन्छ।"
                ),
                "fields": ("release_version", "release_date", "release_notes", "download_url"),
            },
        ),
        (
            "मिडिया (Media)",
            {
                "description": "परियोजनाको स्क्रिनसट/कभर छवि देखाउने URL यहाँ राख्नुहोस्।",
                "fields": ("screenshot_url",),
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "owner":
            _disable_related_widget_icons(
                formfield,
                aria_label=(
                    "जिम्मेवार प्रयोगकर्ता छान्नुहोस् — यो परियोजना व्यवस्थापन गर्ने "
                    "प्रयोगकर्ता (वैकल्पिक, खाली राख्न मिल्छ)।"
                ),
            )
        elif db_field.name == "tags":
            _disable_related_widget_icons(
                formfield,
                aria_label="ट्याग(हरू) छान्नुहोस् — एकभन्दा बढी छान्न सकिन्छ।",
            )
        return formfield


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "due_date", "completed_at")
    list_filter = ("status",)
    search_fields = ("title", "project__title")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "project":
            _disable_related_widget_icons(
                formfield, aria_label="यो माइलस्टोन कुन परियोजनासँग सम्बन्धित छ भनेर छान्नुहोस्।"
            )
        return formfield
