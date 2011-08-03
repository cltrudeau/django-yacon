from django.core.management.base import BaseCommand, CommandError

from yacon.models.hierarchy import Site

class Command(BaseCommand):
    def handle(self, *args, **options):
        name='Localhost Site'
        url='localhost:8000'

        site = Site.create_site(name, url, ['en'])
