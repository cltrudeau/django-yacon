from django.core.management.base import BaseCommand, CommandError

from yacon.models.site import Site

class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError(('Must provide two arguments: "name" and '
                '"domain"'))

        Site.create_site(name=args[0], domain=args[1])
