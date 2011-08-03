from django.core.management.base import BaseCommand, CommandError

from yacon.models.site import Site

class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('Must provide two arguments: "site name" and '\
                + '"site URL"')

        Site.create_site(name=args[0], base_url=args[1])
