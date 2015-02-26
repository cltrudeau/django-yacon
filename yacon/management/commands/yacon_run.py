from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        if len(args) != 1:
            print 'yacon_run -- run a given file within the django shell env'
            print 'usage:'
            print '   manage.py yacon_run filename'
            quit()

        execfile(args[0])
