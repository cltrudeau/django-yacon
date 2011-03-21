# groupsq.models.py
# blame ctrudeau chr(64) arsensa.com

# GroupSq (Group Squared) works with Django auth to provide groups of groups
# and classes of groups functionality.

from django.contrib.auth.models import User, Group
from django.db import models

# ============================================================================

class GroupOfGroups_Base(models.Model):
    """Base class for a group of groups that contains users, groups or groups 
    of groups."""

    # GofG can contain django users, django groups or another GofG
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    group_of_groups = models.ManyToManyField(
        'yacon.GroupOfGroups', blank=True)

    class Meta:
        app_label = 'yacon'
        abstract = True

    # -----------------------------------------
    # Settr Methods
    def add(self, item):
        if isinstance(item, User):
            self.users.add(item)
            self.save()
        elif isinstance(item, Group):
            self.groups.add(item)
            self.save()
        elif isinstance(item, GroupOfGroups):
            self.group_of_groups.add(item)
            self.save()
        else:
            raise AttributeError(
                'parameter to add() was not a User, Group or GroupOfGroups')

    # -----------------------------------------
    # Gettr Methods

    def has_user(self, user):
        """Searches for users recursively within all relations for this GofG
        and returns true if the passed in user is found."""

        # check if the requested user is in our list
        if user in self.users.all():
            return True

        # check if the requested user is in one of our django groups
        for group in self.groups.all():
            if user in group.user_set.all():
                return True

        # go through our recursive relationships and try and find the user
        for gog in self.group_of_groups.all():
            if gog.has_user(user):
                return True

        return False

    def list_users(self):
        """Returns a list of users belonging to this GofG or any of its
        sub-relations"""
        users = []
        users.extend(list(self.users.all()))

        for group in self.groups.all():
            users.extend(list(group.user_set.all()))

        # recurse through any sub relations and find all users
        for gog in self.group_of_groups.all():
            users.extend(gog.list_users())

        return users


class GroupOfGroups(GroupOfGroups_Base):
    """Defines a group of groups that is unique by name"""

    name = models.CharField(max_length=80, unique=True)


class OwnedGroupOfGroups(GroupOfGroups_Base):
    """Defines a group of groups that is owned by a user.  The name parameter
    is no longer needed to be unique.  Used for things like "friends of
    George". """

    owner = models.ForeignKey(User, related_name='ownedgroupofgroups_owner_set')
    name = models.CharField(max_length=80)
