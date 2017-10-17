from django.core.management.base import BaseCommand

from yacon.models.site import Site

class Command(BaseCommand):
    help = 'Adds a new site to your yacon instance'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('domain', type=str)

    def handle(self, *args, **options):
        Site.create_site(name=options['name'], domain=options['domain'])
