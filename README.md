# Jay Nepal IT प्रविधि — पूर्ण प्रोजेक्ट (Frontend + Backend)

```
jaynepal-it-full/
├── frontend/          ← स्टाटिक वेबसाइट (HTML/CSS/JS + Bootstrap 5)
│   ├── index.html
│   ├── about.html
│   ├── projects.html
│   ├── login.html
│   ├── news.html
│   ├── coming-soon.html
│   └── assets/
│       ├── css/style.css
│       └── js/ (api-config.js, roadmap.js, news.js, projects.js, home.js, main.js)
│
└── backend/           ← Django + MySQL API
    ├── manage.py
    ├── requirements.txt
    ├── .env.example
    ├── config/         (settings, urls, wsgi/asgi)
    └── apps/
        ├── accounts/   (Users, roles, ACL, auth)
        ├── projects/   (Projects, milestones, tags)
        ├── newsfeed/   (News + version-control revisions)
        └── roadmaps/   (Roadmap items + release tracker)
```

## चलाउने क्रम

**१. Backend पहिले चलाउनुहोस्** (विस्तृत निर्देशन `backend/README.md` मा छ):

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # अनि MySQL credentials भर्नुहोस्
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
→ Backend: `http://127.0.0.1:8000` | Admin: `http://127.0.0.1:8000/admin/`

**२. अनि frontend चलाउनुहोस्** (नयाँ टर्मिनल/VS Code Live Server मा):

```bash
cd frontend
python -m http.server 5500
```
→ ब्राउजरमा खोल्नुहोस्: `http://127.0.0.1:5500`

⚠️ `frontend/index.html` लाई सिधै डबल-क्लिक गरेर नखोल्नुहोस् — API/login काम गर्दैन। माथिकै तरिकाले सर्भरबाट खोल्नुपर्छ।

दुबै (backend `runserver` + frontend सर्भर) **एकैसाथ** चलिरहेको हुनुपर्छ।

## Admin बाट डेटा थप्ने

Website मा data देखिनका लागि `http://127.0.0.1:8000/admin/` बाट कम्तीमा यी थप्नुहोस्:
- **Roadmaps → Roadmap items** — होमपेज/आगामी पेजको रोडम्याप बोर्डमा देखिन्छ
- **Newsfeed → News posts** — समाचार पेज **र गृहपृष्ठको "हाम्रो समाचार" प्रिभ्यु** (पछिल्लो ३ वटा) मा देखिन्छ
- **Projects → Projects** (+ Milestones) — Projects पेजमा देखिन्छ; "Is featured" ✓ गरेको Project मात्र गृहपृष्ठको "हाम्रा प्रमुख परियोजनाहरू" र projects.html को साइडबारमा देखिन्छ

गृहपृष्ठ अब पूर्ण रूपमा डाइनामिक छ — Roadmap, प्रमुख परियोजनाहरू, र समाचार प्रिभ्यु तीनवटै backend बाट लाइभ आउँछन्। Admin मा नयाँ थपेपछि गृहपृष्ठ refresh गरे तुरुन्तै देखिन्छ।
