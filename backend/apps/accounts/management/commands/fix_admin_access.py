"""
apps/accounts/management/commands/fix_admin_access.py
---------------------------------------------------------------
अस्थायी (temporary) एक-पटके command — Railway Console पहुँच
नभएको बेला, Deploy Logs मार्फतै (जुन Railway ले हरेक deploy मा
आफैं देखाउँछ) account जानकारी हेर्न र superuser password ठीक
गर्न बनाइएको।

⚠️ महत्त्वपूर्ण: यो command काम सकिएपछि, Procfile बाट यसलाई चलाउने
लाइन हटाउनुहोस् — नत्र हरेक नयाँ deploy मा फेरि password त्यही
default मा फर्किरहन्छ, जुन सुरक्षाका लागि राम्रो होइन।
---------------------------------------------------------------
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

TARGET_USERNAME = "yawanjung"
TARGET_PASSWORD = "yaman@10"


class Command(BaseCommand):
    help = "सबै account list गर्ने र yawanjung superuser को password ठीक गर्ने (Deploy Logs मार्फत)।"

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("FIX-ADMIN-ACCESS: हालका सबै account हरू")
        self.stdout.write("=" * 60)

        users = User.objects.all().order_by("id")
        if not users.exists():
            self.stdout.write("कुनै पनि account फेला परेन।")
        for u in users:
            self.stdout.write(
                f"  id={u.id} | username={u.username!r} | email={u.email!r} "
                f"| is_superuser={u.is_superuser} | is_staff={u.is_staff} "
                f"| is_active={u.is_active}"
            )

        self.stdout.write("-" * 60)

        user, created = User.objects.get_or_create(
            username=TARGET_USERNAME,
            defaults={
                "email": f"{TARGET_USERNAME}@jaynepalit.com",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(TARGET_PASSWORD)
        # यदि User model मा is_email_verified जस्तो field छ भने, admin
        # login गर्नु email verification मा भर पर्दैन (त्यो custom login
        # view को नियम हो, Django admin को होइन) — त्यसैले यो छुनु पर्दैन।
        user.save()

        action = "नयाँ superuser बनाइयो" if created else "existing account फेला पर्‍यो, password अपडेट गरियो"
        self.stdout.write(
            f"FIX-ADMIN-ACCESS: {action} — username={TARGET_USERNAME!r}, "
            f"password={TARGET_PASSWORD!r}, email={user.email!r}"
        )
        self.stdout.write("=" * 60)
        self.stdout.write("अब /admin/ मा माथिको username/password ले login गर्नुहोस्।")
        self.stdout.write("=" * 60)
