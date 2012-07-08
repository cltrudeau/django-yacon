from django.core.management.base import BaseCommand

from yacon.models.common import Language
from yacon.models.site import Site

class Command(BaseCommand):
    def handle(self, *args, **options):
        name='Localhost Site'
        domain='localhost:8000'

        language = Language.factory(name='English', identifier='en')
        Site.create_site(name, domain, languages=[language])
