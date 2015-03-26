# create_test_admin.py
#
# Creates an admin user, done here so it can be automated as part of the reset
# script

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from yacon.models.users import UserProfile

class Command(BaseCommand):
    def handle(self, *args, **options):
        UserProfile.create('admin', 'AdminFirst', 'AdminLast',
            'admin@admin.com', 'admin', is_superuser=True, is_staff=True)
