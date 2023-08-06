from django.core.management.base import BaseCommand

from event.models import Calendar


class Command(BaseCommand):
    help = "Update calendar events via API"

    def handle(self, *args, **options):
        for cal in Calendar.objects.filter(auto_update=True):
            cal.update_events()