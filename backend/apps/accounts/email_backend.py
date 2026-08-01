"""
apps/accounts/email_backend.py
---------------------------------------------------------------
Resend (https://resend.com) को HTTP API मार्फत इमेल पठाउने custom
Django email backend — SMTP (smtplib/socket) को साटो।

किन चाहियो: Railway (र धेरैजसो free/cheap PaaS) ले outbound SMTP
port (587/465/25) लाई spam-रोकथामका लागि block गर्छ। Production
log मा देखिएको "OSError: [Errno 101] Network is unreachable" यही
block को प्रत्यक्ष प्रमाण हो — App Password/credential ठीक भए पनि
SMTP जडान नै हुन सक्दैन। HTTP API भने port 443 (HTTPS) बाटै जान्छ,
जुन कहिल्यै block हुँदैन (नत्र website नै चल्दैनथ्यो)।

प्रयोग गर्ने तरिका (Railway Variables मा):
    EMAIL_BACKEND = apps.accounts.email_backend.ResendAPIEmailBackend
    RESEND_API_KEY = <resend.com बाट लिएको API key>
    DEFAULT_FROM_EMAIL = <resend मा verify गरेको domain/email>

Resend सेटअप (छोटकरीमा):
    1. https://resend.com मा Sign up गर्नुहोस् (Free — महिनाको ३,०००
       इमेल, दिनको १०० सम्म)।
    2. आफ्नो domain (jaynepalit.com) verify गर्नुहोस् (Resend ले DNS
       record दिन्छ — Cloudflare मा थप्नुहोस्, हामीले पहिल्यै त्यहीँ
       काम गरिरहेका छौं)। domain verify नगरी पनि Resend को आफ्नै
       test domain (onboarding@resend.dev) बाट पठाउन मिल्छ, तर त्यो
       प्रयोगकर्ताको Gmail मा spam मा जान सक्छ — आफ्नै domain verify
       गर्नु सिफारिस गरिन्छ।
    3. "API Keys" मा गएर नयाँ key बनाउनुहोस्, त्यो Railway को
       RESEND_API_KEY मा राख्नुहोस्।
---------------------------------------------------------------
"""
import json
import logging
import os
import urllib.error
import urllib.request

from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"
REQUEST_TIMEOUT_SECONDS = 10


class ResendAPIEmailBackend(BaseEmailBackend):
    """Django को standard EmailMessage वस्तुहरू लिएर, Resend को HTTP
    API मार्फत पठाउने। send_mail(), EmailMessage.send() सबैसँग उस्तै
    काम गर्छ — केवल transport SMTP बाट HTTPS मा बदलिएको छ।"""

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        api_key = os.environ.get("RESEND_API_KEY", "")
        if not api_key:
            message = "RESEND_API_KEY सेट गरिएको छैन — Railway Variables मा राख्नुहोस्।"
            if self.fail_silently:
                logger.error(message)
                return 0
            raise ValueError(message)

        sent_count = 0
        for message in email_messages:
            payload = {
                "from": message.from_email,
                "to": list(message.to),
                "subject": message.subject,
                "text": message.body,
            }
            if message.cc:
                payload["cc"] = list(message.cc)
            if message.bcc:
                payload["bcc"] = list(message.bcc)

            data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(
                RESEND_API_URL,
                data=data,
                method="POST",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    # महत्त्वपूर्ण: Resend को API Cloudflare ले सुरक्षित गरेको छ।
                    # urllib को default User-Agent ("Python-urllib/x.x") लाई
                    # Cloudflare ले bot/script ठानेर block गर्छ (error code
                    # 1010) — यो सामान्य browser जस्तो User-Agent राखेर
                    # त्यो block बाट जोगिने।
                    "User-Agent": "JayNepalIT-Django-Mailer/1.0",
                    "Accept": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                    if 200 <= response.status < 300:
                        sent_count += 1
                    else:
                        raise RuntimeError(f"Resend API ले status {response.status} फर्कायो।")
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                logger.error("Resend API त्रुटि (%s): %s", exc.code, body)
                if not self.fail_silently:
                    raise
            except Exception:
                logger.exception("Resend API मार्फत इमेल पठाउन सकिएन।")
                if not self.fail_silently:
                    raise

        return sent_count
