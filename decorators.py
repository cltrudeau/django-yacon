# yacon.decorators.py

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.http import Http404

# ============================================================================

def superuser_required(target):
    """Decorator that ensures user is logged in and has superuser bit set."""

    @wraps(target)
    def wrapper(*args, **kwargs):
        request = args[0]

        # test goes here
        if request.user.is_authenticated() and request.user.is_superuser:
            return target(*args, **kwargs)

        # redirect to login page defined in settings with the current URL as
        # the "next" path
        return redirect_to_login(request.build_absolute_uri())
    return wrapper


def post_required(target):
    """Decorator for views that must only be called as POST"""
    @wraps(target)
    def wrapper(*args, **kwargs):
        request = args[0]
        if request.method != 'POST':
            raise Http404('GET method not supported')

        return target(*args, **kwargs)
    return wrapper
