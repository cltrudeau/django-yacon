# Creates user accounts and data for testing and demos
from django.core.management.base import BaseCommand

from yacon.models.site import Site


# =============================================================================

class Command(BaseCommand):
    def handle(self, *args, **options):
