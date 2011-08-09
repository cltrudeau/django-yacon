from django.core.management.base import BaseCommand, CommandError

from yacon.models.language import Language
from yacon.models.site import Site

class Command(BaseCommand):
    def handle(self, *args, **options):
        name='Localhost Site'
        url='localhost:8000'

        language = Language.factory(name='English', identifier='en')
        site = Site.create_site(name, url, languages=[language])
