# Jay Nepal IT प्रविधि — Django Backend

## संरचना (Structure)

```
jaynepal_backend/
├── manage.py
├── requirements.txt
├── .env.example
├── config/                # Project-level settings, urls, wsgi/asgi
└── apps/
    ├── accounts/           # Users, roles, ACL, profile, auth
    ├── projects/           # Projects, milestones, tags
    ├── newsfeed/           # News posts + version-control revisions
    └── roadmaps/           # Roadmap items + release tracker
```

हरेक app भित्र `models.py` (data), `selectors.py` (read-only queries),
`services.py` (write/business logic), `views.py` (thin JSON endpoints),
`admin.py`, र `urls.py` छुट्टाछुट्टै राखिएको छ (Separation of Concerns)।

## सेटअप

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # अनि .env मा आफ्नो MySQL credentials भर्नुहोस्

# MySQL मा डेटाबेस बनाउनुहोस् (एकपटक मात्र):
#   CREATE DATABASE jaynepal_it_db CHARACTER SET utf8mb4;

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Admin प्यानल: `http://127.0.0.1:8000/admin/`

## API Endpoints (हाल उपलब्ध)

| Method | Path | विवरण |
|---|---|---|
| POST | `/api/accounts/signup/` | नयाँ खाता बनाउने |
| POST | `/api/accounts/login/` | लगइन (session-based) |
| POST | `/api/accounts/logout/` | लगआउट |
| GET | `/api/accounts/me/` | हालको प्रयोगकर्ता जानकारी |
| GET | `/api/projects/` | सबै परियोजना (`?type=` र `?status=` फिल्टर) |
| GET | `/api/projects/featured/` | होमपेजका featured परियोजना |
| GET | `/api/projects/<slug>/` | एउटा परियोजनाको विवरण |
| GET | `/api/news/` | समाचार फिड (`?category=` फिल्टर) |
| GET | `/api/news/<slug>/` | एउटा समाचार + रिभिजन इतिहास |
| GET | `/api/roadmap/` | रोडम्याप बोर्ड (`?status=` फिल्टर) |

Response shape frontend का `assets/js/roadmap.js` र `assets/js/news.js`
भित्रका mock arrays सँग मिल्ने गरी design गरिएको छ — त्यहाँको
`FETCH_ROADMAP_DATA()`/`FETCH_NEWS_DATA()` लाई माथिका endpoint बाट
`fetch()` गर्ने बनाउनुभयो भने markup-रेन्डरिङ कोडमा ठूलो परिवर्तन
गर्नु पर्दैन।

## थप गर्न बाँकी (अर्को चरणमा)

- Token-based auth (जस्तै DRF + SimpleJWT) — हाल session-based
- Frontend फारमहरू (`login.html`, `subscribe`) लाई माथिका endpoint सँग सिधै `fetch()` जोड्ने
- Production मा `DEBUG=False`, वास्तविक `DJANGO_SECRET_KEY`, र `ALLOWED_HOSTS` सेट गर्ने
