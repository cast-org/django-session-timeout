from django.core.management.base import BaseCommand
from ...shared import expire_sessions

class Command(BaseCommand):
    help = (
        "Can be run as a cronjob or directly to clean out expired sessions "
        "(only with the database backend at the moment)."
    )

    def handle(self, **options):
        expire_sessions()


