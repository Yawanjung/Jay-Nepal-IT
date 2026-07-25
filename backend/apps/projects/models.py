"""
apps/projects/models.py
---------------------------------------------------------------
Projects: परियोजना (Pariyojana) को विवरण, भित्र रहेका माइलस्टोनहरू,
र विभिन्न विधाका ट्यागहरू (कृषि-टेक, शैक्षिक पोर्टल, स्वास्थ्य प्रणाली)।
---------------------------------------------------------------
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    """परियोजना विधा/ट्याग — जस्तै: कृषि-टेक, शैक्षिक पोर्टल, स्वास्थ्य प्रणाली।"""

    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="ट्यागको नाम",
        help_text="छोटो, स्पष्ट नाम लेख्नुहोस्, जस्तै: 'कृषि-टेक'।",
    )
    slug = models.SlugField(
        max_length=90,
        unique=True,
        blank=True,
        verbose_name="URL स्लग",
        help_text="खाली नै छाड्नुहोस् — नामबाट स्वतः बन्नेछ।",
    )
    color_hex = models.CharField(
        max_length=7,
        default="#1f7a7d",
        verbose_name="रङ (Hex कोड)",
        help_text="ट्याग देखाउँदा प्रयोग हुने रङ (जस्तै: #e8772e)।",
    )

    class Meta:
        verbose_name = "ट्याग"
        verbose_name_plural = "ट्यागहरू"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Project(models.Model):
    """मुख्य परियोजना मोडेल।"""

    class Category(models.TextChoices):
        SOFTWARE = "software", "सफ्टवेयर"
        MOBILE_APP = "mobile_app", "मोबाइल एप"
        WEB_PORTAL = "web_portal", "वेब पोर्टल"
        GAME = "game", "गेम"

    class Status(models.TextChoices):
        PLANNED = "planned", "योजनामा"
        IN_PROGRESS = "in_progress", "विकासमा"
        TESTING = "testing", "परीक्षणमा"
        ACTIVE = "active", "सक्रिय"
        ARCHIVED = "archived", "अभिलेखमा"

    class Priority(models.TextChoices):
        LOW = "low", "न्यून"
        MEDIUM = "medium", "मध्यम"
        HIGH = "high", "उच्च"
        CRITICAL = "critical", "अत्यावश्यक"

    title = models.CharField(
        max_length=200,
        verbose_name="परियोजनाको नाम",
        help_text="परियोजनाको पूरा नाम यहाँ लेख्नुहोस्, जस्तै: 'ASW - A Separate World'।",
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name="URL स्लग",
        help_text="वेब ठेगानामा देखिने छोटो कोड। खाली नै छाड्नुहोस् — नामबाट स्वतः बन्नेछ।",
    )
    summary = models.CharField(
        max_length=300,
        verbose_name="छोटो सारांश",
        help_text="छोटो विवरण — कार्ड/लिस्टमा देखाउनका लागि (१-२ वाक्य)।",
    )
    description = models.TextField(
        blank=True,
        verbose_name="विवरण (साधारण/पुरानो)",
        help_text=(
            "यो पुरानो/साधारण विवरण फिल्ड हो। नयाँ परियोजनाका लागि तल दिइएका "
            "छुट्टाछुट्टै फिल्डहरू (परिचय, उद्देश्य, मुख्य विशेषता, लक्षित समूह) "
            "भर्नु सिफारिस गरिन्छ; यो फिल्ड खाली राख्दा पनि हुन्छ।"
        ),
    )

    # --- संरचित विवरण (Structured Description) ---
    introduction = models.TextField(
        blank=True,
        verbose_name="परिचय (Introduction)",
        help_text="यो परियोजना के हो भन्ने छोटो परिचय अनुच्छेद यहाँ लेख्नुहोस्।",
    )
    objective = models.TextField(
        blank=True,
        verbose_name="उद्देश्य (Objective)",
        help_text="यो परियोजना किन बनाइयो, यसको मुख्य लक्ष्य के हो भनेर लेख्नुहोस्।",
    )
    key_features = models.TextField(
        blank=True,
        verbose_name="मुख्य विशेषताहरू (Key Features)",
        help_text="हरेक विशेषता छुट्टै लाइनमा लेख्नुहोस् — एक लाइनमा एउटा मात्र विशेषता।",
    )
    target_audience = models.TextField(
             blank=True,
        verbose_name="लक्षित प्रयोगकर्ता समूह (Target Audience)",
        help_text="यो परियोजना कसका लागि हो, जस्तै: 'किसान र कृषि व्यवसायीहरू'।",
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.WEB_PORTAL,
        db_index=True,
        verbose_name="श्रेणी (Category)",
        help_text="यो परियोजना कुन प्रकारको हो — सफ्टवेयर, मोबाइल एप, वेब पोर्टल, वा गेम।",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
        db_index=True,
        verbose_name="हालको अवस्था (Status)",
        help_text="परियोजना योजनामा, विकासमा, परीक्षणमा, सक्रिय, वा अभिलेखमा — कुन चरणमा छ छान्नुहोस्।",
    )
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="प्रगति (%)",
        help_text="परियोजनाको प्रगति प्रतिशतमा (0 देखि 100 सम्म कुनै अङ्क)।",
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
        verbose_name="प्राथमिकता (Priority)",
        help_text="यो परियोजनालाई हामीले कति प्राथमिकतामा राखेका छौं भन्ने तह छान्नुहोस्।",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="projects",
        blank=True,
        verbose_name="ट्यागहरू (Tags)",
        help_text="सान्दर्भिक ट्याग(हरू) छान्नुहोस् (जस्तै: कृषि-टेक)। एकभन्दा बढी छान्न सकिन्छ।",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_projects",
        verbose_name="जिम्मेवार प्रयोगकर्ता (Owner)",
        help_text="यो परियोजना व्यवस्थापन गर्ने प्रयोगकर्ता (वैकल्पिक — खाली राख्न मिल्छ)।",
    )
    icon_emoji = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="इमोजी/आइकन",
        help_text="कार्डमा देखाउने इमोजी/आइकन, जस्तै 🚜",
    )

    # --- रिलिज जानकारी (Release Information) ---
    release_version = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="रिलिज संस्करण (Version)",
        help_text="जस्तै: v1.2.0",
    )
    release_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="रिलिज/लक्षित मिति",
        help_text="वास्तविक रिलिज मिति वा लक्षित मिति (ETA)।",
    )
    release_notes = models.TextField(
        blank=True,
        verbose_name="रिलिज नोटहरू (Changelog)",
        help_text="रिलिज/परिवर्तन नोटहरू (changelog)।",
    )
    download_url = models.URLField(
        blank=True,
        verbose_name="डाउनलोड / लाइभ साइट लिङ्क",
        help_text=(
            "Testing वा Active भएपछि यही लिङ्क प्रयोग हुन्छ — श्रेणी 'वेब पोर्टल' "
            "भए 'लाइभ साइट हेर्नुहोस्' र अरू (सफ्टवेयर/मोबाइल एप/गेम) भए "
            "'डाउनलोड गर्नुहोस्' बटन स्वतः देखिन्छ।"
        ),
    )
    screenshot_url = models.URLField(
        blank=True,
        verbose_name="स्क्रिनसट/छवि URL",
        help_text="परियोजनाको स्क्रिनसट वा कभर छवि देखाउने URL (वैकल्पिक)।",
    )

    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Featured (गृहपृष्ठमा देखाउने?)",
        help_text="✓ गरे यो परियोजना गृहपृष्ठ र Projects पेजको माथिल्लो भागमा देखिनेछ।",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="बनेको मिति")
    updated_at = models.DateTimeField(auto_now=True, db_index=True, verbose_name="अपडेट भएको मिति")

    class Meta:
        verbose_name = "परियोजना"
        verbose_name_plural = "परियोजनाहरू"
        ordering = ["-is_featured", "-updated_at"]
        indexes = [
            models.Index(fields=["status", "category"]),
            models.Index(fields=["status", "priority"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_downloadable(self) -> bool:
        """Testing/Active अवस्थामा र लिङ्क भरिएको भए मात्र Action बटन (Download/Visit) देखाउने।"""
        return bool(self.download_url) and self.status in (
            self.Status.TESTING,
            self.Status.ACTIVE,
        )

    @property
    def action_kind(self) -> str:
        """परियोजनाको प्रकृति अनुसार बटनको किसिम — वेब पोर्टल भए 'visit', अरू भए 'download'।"""
        return "visit" if self.category == self.Category.WEB_PORTAL else "download"

    @property
    def action_label(self) -> str:
        """बटनमा देखिने पाठ — प्रकृति अनुसार 'लाइभ साइट हेर्नुहोस्' वा 'डाउनलोड गर्नुहोस्'।"""
        return "लाइभ साइट हेर्नुहोस्" if self.action_kind == "visit" else "डाउनलोड गर्नुहोस्"

    @property
    def key_features_list(self):
        """key_features फिल्डलाई लाइन-लाइन गरी सूचीमा बदल्ने (खाली लाइनहरू हटाएर)।"""
        return [line.strip() for line in self.key_features.splitlines() if line.strip()]

    @property
    def is_roadmap_visible(self) -> bool:
        """Coming Soon/Roadmap पेजमा देखिने योग्य अवस्थाहरू (सक्रिय/अभिलेख होइन)।"""
        return self.status in (
            self.Status.PLANNED,
            self.Status.IN_PROGRESS,
            self.Status.TESTING,
        )


class Milestone(models.Model):
    """परियोजना भित्रका माइलस्टोनहरू।"""

    class Status(models.TextChoices):
        PLANNED = "planned", "योजनामा"
        IN_PROGRESS = "in_progress", "विकासमा"
        TESTING = "testing", "परीक्षणमा"
        COMPLETED = "completed", "सफल समापन"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="milestones",
        verbose_name="परियोजना",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="माइलस्टोनको नाम",
        help_text="माइलस्टोनको छोटो नाम लेख्नुहोस्, जस्तै: 'Beta रिलिज'।",
    )
    description = models.TextField(
        blank=True,
        verbose_name="विवरण",
        help_text="यो माइलस्टोनमा के हुन्छ भन्ने छोटो व्याख्या (वैकल्पिक)।",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
        db_index=True,
        verbose_name="अवस्था",
        help_text="यो माइलस्टोन हाल कुन अवस्थामा छ भनेर छान्नुहोस्।",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="लक्षित मिति",
        help_text="यो माइलस्टोन कहिलेसम्म पूरा गर्ने लक्ष्य हो (वैकल्पिक)।",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="पूरा भएको मिति/समय",
        help_text="यो माइलस्टोन वास्तवमा कहिले पूरा भयो — पूरा भइसकेपछि मात्र भर्नुहोस्।",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="देखिने क्रम",
        help_text="सानो अङ्क भएको माइलस्टोन पहिले देखिन्छ (जस्तै: 0, 1, 2...)।",
    )

    class Meta:
        verbose_name = "माइलस्टोन"
        verbose_name_plural = "माइलस्टोनहरू"
        ordering = ["project", "order", "due_date"]
        indexes = [
            models.Index(fields=["project", "status"]),
        ]

    def __str__(self):
        return f"{self.project.title} — {self.title}"
