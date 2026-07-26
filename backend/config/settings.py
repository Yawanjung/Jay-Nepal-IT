"""
जय नेपाल आईटी प्रविधि — Django Settings
Separation of Concerns: settings यहाँ मात्र केन्द्रित छ; business logic
हरेक app को services.py/selectors.py मा राखिन्छ, views.py मा होइन।
"""

import os
from pathlib import Path
# .env फाइल लोड गर्न आवश्यक लाइब्रेरी
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------
# .env फाइल लोड गर्ने — यो नभई os.environ.get() ले .env भित्रका
# कुनै पनि भ्यालु (जस्तै DB_PASSWORD) पढ्दैन।
# ---------------------------------------------------------------
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------
# सुरक्षा / वातावरण (Environment) — production मा .env बाट लोड गर्नुहोस्
# ---------------------------------------------------------------
# अब कुनै पनि डिफल्ट पासवर्ड कोडमा राखिएको छैन
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ---------------------------------------------------------------
# Installed Apps
# ---------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # थर्ड-पार्टी
    "corsheaders",
    # आन्तरिक एपहरू
    "apps.accounts",
    "apps.projects",
    "apps.newsfeed",
    "apps.roadmaps",
    "apps.services",
    "apps.team",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise — SecurityMiddleware पछि, अरू जुनसुकै भन्दा माथि हुनुपर्छ।
    # DEBUG=False (production) मा Django dev server ले static/admin CSS-JS
    # स्वतः serve गर्न छोड्छ; WhiteNoise ले त्यो काम gunicorn मार्फत नै
    # (छुट्टै Nginx/CDN नभए पनि) सुरक्षित र सजिलै गर्छ।
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------
# डेटाबेस — MySQL (उच्च रिलेशनल र अनुक्रमित/Normalized Schema)
# ---------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ---------------------------------------------------------------
# कस्टम प्रयोगकर्ता मोडेल
# ---------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------
# अन्तर्राष्ट्रियकरण
# ---------------------------------------------------------------
LANGUAGE_CODE = "ne"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------
# स्ट्याटिक फाइलहरू (Bootstrap 5 फ्रन्टइन्ड + Django Admin CSS/JS)
# ---------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "frontend_assets"]
STATIC_ROOT = BASE_DIR / "staticfiles"

if DEBUG:
    # dev मा collectstatic नचलाई नै runserver ले सिधै फाइल फेला पारोस्।
    WHITENOISE_USE_FINDERS = True
else:
    # production मा compressed + cache-busting hashed filename (collectstatic पछि)।
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------
# CORS र CSRF सेटिङहरू
# ---------------------------------------------------------------
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500"
).split(",")
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500"
).split(",")
CSRF_COOKIE_HTTPONLY = False
# नोट: Frontend (jaynepalit.com/Firebase) र Backend (Railway) फरक-फरक
# domain मा भएकोले (cross-origin), production मा "Lax" cookie ले काम
# गर्दैन — browser ले cross-site fetch मा Lax cookie नै नपठाई CSRF
# verification बारम्बार फेल हुन्थ्यो (403)। "None" ले cross-origin मा
# पनि cookie पठाउन दिन्छ, तर यसलाई "Secure=True" (HTTPS) सँगै मात्र
# प्रयोग गर्न मिल्छ — त्यसैले local HTTP dev मा भने "Lax" नै राखिएको छ
# (नत्र browser ले "None" cookie लाई HTTP मा पूर्ण रूपमा अस्वीकार गर्छ)।
CSRF_COOKIE_SAMESITE = "Lax" if DEBUG else "None"
SESSION_COOKIE_SAMESITE = "Lax" if DEBUG else "None"

# ---------------------------------------------------------------
# इमेल (Email verification का लागि)
# ---------------------------------------------------------------
# Development मा: console मा नै इमेल देखिन्छ (कुनै SMTP चाहिँदैन)
# Production मा: .env मा EMAIL_BACKEND र SMTP credentials राख्नुहोस्
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@jaynepalit.com")

# Verification लिङ्क बनाउँदा प्रयोग हुने frontend को ठेगाना
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://127.0.0.1:5500")

# Production मा HTTPS-only कुकी
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ---------------------------------------------------------------
# सुरक्षा हेडरहरू
# ---------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ---------------------------------------------------------------
# Admin प्यानल
# ---------------------------------------------------------------
ADMIN_URL_PATH = os.environ.get("DJANGO_ADMIN_URL", "admin/")
# ---------------------------------------------------------------
# Rate Limit Settings (django-ratelimit का लागि)
# ---------------------------------------------------------------
# १ मिनेटमा ५ पटकसम्म लगइन प्रयास
LOGIN_RATE_LIMIT = '5/m'
# १ मिनेटमा ३ पटकसम्म साइनअप प्रयास
SIGNUP_RATE_LIMIT = '3/m'

# (वैकल्पिक) यदि धेरै रिक्वेस्ट आएपछि के गर्ने भन्ने सेटिङ
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default' # यदि तपाईंले पछि Redis प्रयोग गर्नुभयो भने यो काम लाग्छ