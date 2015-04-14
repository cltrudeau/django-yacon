# groupsq.models.py
#
# GroupSq (Group Squared) works with Django auth to provide groups of groups
# and classes of groups functionality.
import logging

from django.contrib.auth.models import User, Group
from django.db import models

from yacon.models.common import TimeTrackedModel

logger = logging.getLogger(__name__)

# ============================================================================

class CycleDetected(Exception):
    def __init__(self, chain):
        self.chain = chain
        super(CycleDetected, self).__init__()


def _descend_cycle(gog, seen):
    for g in gog.group_of_groups.all():
        if g.id in seen:
            seen.append(g.id)
            raise CycleDetected(seen)

        yield g
        seen.append(g.id)
        for subg in _descend_cycle(g, seen):
            yield subg


def cycle_detect_iterator(gog):
    """Iterator that goes through a GroupOfGroups' nested GroupOfGroups
    field.  If a cycle is an exception is raised.

    :raises: CycleDetected
    """
    seen = [gog.id]
    return _descend_cycle(gog, seen)


class GroupOfGroups_Base(TimeTrackedModel):
    """Base class for a group of groups that contains users, groups or groups 
    of groups."""

    # GofG can contain django users, django groups or another GofG
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    group_of_groups = models.ManyToManyField(
        'yacon.GroupOfGroups', blank=True)

    class Meta:
        app_label = 'yacon'
        verbose_name = 'MetaPage'
        abstract = True

    # -----------------------------------------
    # Settr Methods
    def add(self, item):
        if isinstance(item, User):
            self.users.add(item)
        elif isinstance(item, Group):
            self.groups.add(item)
        elif isinstance(item, GroupOfGroups):
            self.group_of_groups.add(item)
        else:
            raise AttributeError(
                'parameter to add() was not a User, Group or GroupOfGroups')

        self.save() # force an update of the timestamp

    # -----------------------------------------
    # Gettr Methods

    def _safe_list_users(self):
        """Generator for the non-recursive portion of users in a GofG"""
        for u in self.users.all():
            yield u

        for group in self.groups.all():
            for u in group.user_set.all():
                yield u

    def list_users(self):
        """Generator that returns all users nested within sub-relations"""
        users = set()
        users.update(self._safe_list_users())

        # recurse through any sub relations and find all users
        try:
            for gog in cycle_detect_iterator(self):
                users.update(gog._safe_list_users())
        except CycleDetected as e:
            logger.warning('Cycle detected in %s chain was: %s', 
                self, e.chain)

        return list(users)

    def has_user(self, user):
        """Searches for users recursively within all relations for this GofG
        and returns true if the passed in user is found."""
        for u in self._safe_list_users():
            if u == user:
                return True

        # recurse through any sub relations and find all users
        try:
            for gog in cycle_detect_iterator(self):
                for u in gog._safe_list_users():
                    if u == user:
                        return True
        except CycleDetected as e:
            logger.warning('Cycle detected in %s chain was: %s', 
                self, e.chain)

        return False


class GroupOfGroups(GroupOfGroups_Base):
    """Defines a group of groups that is unique by name"""
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        app_label = 'yacon'
        verbose_name = 'Group Of Groups'
        verbose_name_plural = 'Group Of Groups'

    def __unicode__(self):
        return 'GroupOfGroups(id=%s, %s)' % (self.id, self.name)


class OwnedGroupOfGroups(GroupOfGroups_Base):
    """Defines a group of groups that is owned by a user.  The name parameter
    is no longer needed to be unique.  Used for things like "friends of
    George". """

    owner = models.ForeignKey(User, related_name='ownedgroupofgroups_owner_set')
    name = models.CharField(max_length=80)
