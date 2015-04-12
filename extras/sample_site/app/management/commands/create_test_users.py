# create_test_admin.py
#
# Creates an admin user, done here so it can be automated as part of the reset
# script

from django.core.management.base import BaseCommand

from yacon.models.users import UserProfile
from yacon.models.groupsq import GroupOfGroups

class Command(BaseCommand):
    def handle(self, *args, **options):
        UserProfile.create('admin', 'AdminFirst', 'AdminLast',
            'admin@admin.com', 'admin', is_superuser=True, is_staff=True)

        u1 = UserProfile.create('user1', 'User', 'One', 'user1@foo.com', 
            'user1')
        u2 = UserProfile.create('user2', 'User', 'Two', 'user2@foo.com', 
            'user2')
        UserProfile.create('user3', 'User', 'Three', 'user3@foo.com', 'user3')

        g = GroupOfGroups.objects.create(name='group1')
        g.add(u1.user)
        g.add(u2.user)
