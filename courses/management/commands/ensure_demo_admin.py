from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

DEMO_USERNAME = "admin"
DEMO_PASSWORD = "DarsKhane-1404"
DEMO_EMAIL = "admin@example.com"


class Command(BaseCommand):
    help = "اگر کاربر admin وجود نداشته باشد، مدیر آزمایشی می‌سازد."

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(username=DEMO_USERNAME).exists():
            self.stdout.write("demo admin already exists")
            return
        User.objects.create_superuser(DEMO_USERNAME, DEMO_EMAIL, DEMO_PASSWORD)
        self.stdout.write("demo admin created")
