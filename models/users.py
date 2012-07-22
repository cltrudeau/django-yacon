# yacon.models.users.py
import logging, copy

from django.db import models
from django.db import connection
from django.db.utils import IntegrityError
from django.conf import settings
from django.contrib.auth.models import User

from yacon.conf import custom
from yacon.models.common import TimeTrackedModel

logger = logging.getLogger(__name__)

# ============================================================================

class UsernameError(Exception):
    pass


class UserProfileBase(TimeTrackedModel):
    user = models.OneToOneField(User)

    class Meta:
        app_label = 'yacon'
        abstract = True

    @classmethod
    def create(cls, username, first_name, last_name, email, password, **kwargs):
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name

            if 'is_active' in kwargs:
                user.is_active = kwargs.pop('is_active')
            if 'is_staff' in kwargs:
                user.is_staff = kwargs.pop('is_staff')
            if 'is_superuser' in kwargs:
                user.is_superuser = kwargs.pop('is_superuser')

            user.save()
        except IntegrityError:
            # rollback the attempted commit and throw our own error
            connection._rollback()
            err = UsernameError('username %s existed already' % username)
            raise err

        profile = cls(user=user, **kwargs)
        profile.save()
        return profile

    @classmethod
    def create_from_data(cls, data):
        kwargs = copy.copy(data)
        username = kwargs.pop('username')
        first_name = kwargs.pop('first_name')
        last_name = kwargs.pop('last_name')
        email = kwargs.pop('email')
        password1 = kwargs.pop('password1')
        kwargs.pop('password2')

        return cls.create(username, first_name, last_name, email, password1,
            **kwargs)

    def update_profile(self, data):
        """Updates the UserProfile and corresponding User object based on the
        has passed in.  Note: do NOT attempt a password change this way."""
        user_changed = False
        profile_changed = False

        for key, value in data.items():
            if hasattr(self.user, key):
                setattr(self.user, key, value)
                user_changed = True
            elif hasattr(self, key):
                setattr(self, key, value)
                profile_changed = True
            else:
                logger.error('neither profile or profile.user has key "%s"',
                    key)

        try:
            if user_changed:
                self.user.save()
        except IntegrityError:
            connection._rollback()
            raise UsernameError('username %s already existed' %
                data['username'])

        if profile_changed:
            self.save()


class UserProfile(UserProfileBase):
    
    class Meta:
        app_label = 'yacon'
