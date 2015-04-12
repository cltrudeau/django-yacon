# create_test_admin.py
#
# Creates an admin user, done here so it can be automated as part of the reset
# script

from django.core.management.base import BaseCommand

from yacon.models.users import UserProfile

class Command(BaseCommand):
    def handle(self, *args, **options):
        UserProfile.create('admin', 'AdminFirst', 'AdminLast',
            'admin@admin.com', 'admin', is_superuser=True, is_staff=True)

        UserProfile.create('user1', 'User', 'One', 'user1@foo.com', 'user1')
        UserProfile.create('user2', 'User', 'Two', 'user2@foo.com', 'user2')
