# yacon.decorators.py

import logging
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from yacon.utils import FileSpec

logger = logging.getLogger(__name__)

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


def profile_required(target):
    """Ensures request.user has a profile, returns it in the request object.
    Otherwise, raises 404."""
    @wraps(target)
    def wrapper(*args, **kwargs):
        request = args[0]
        try:
            request.profile = request.user.get_profile()
            return target(*args, **kwargs)
        except ObjectDoesNotExist:
            pass

        raise Http404('no profile for user')
    return wrapper


def verify_node(parm, is_file):
    """Decorator to check user's permissions against a file node contained in
    the query string.  Does a request.GET[parm] to check the node in the view.
    A FileSpec is created based on the node, if the permission check passes
    then this spec is put into the request (arg0).  

    If the user is a superuser then the permissions are granted.  If not, the
    node is checked against the user in the request.  A user is only granted
    permission if the node is in under one of "public:users/X" or 
    "private:users/X", where X is the username found in the request.
    
    The "is_file" parameter is a boolean, True indicates the node is a file.
    """
    def decorator(target):
        @wraps(target)
        def wrapper(*args, **kwargs):
            # process options
            request = args[0]
            node = request.GET.get(parm)
            if not node:
                raise Http404('permission denied')

            spec = FileSpec(node, node_is_file=is_file)

            if spec.allowed_for_user(request.user):
                request.spec = spec
                return target(*args, **kwargs)

            logger.error('user %s attempted to access node %s',
                request.user.username, node)

            raise Http404('permission denied')

        return wrapper
    return decorator


def verify_file_url(parm, is_file):
    """Decorator to check user's permissions against a file url contained in 
    the query string.  Does a request.GET[parm] to check the file in the view.
    A FileSpec is created based on the file, if the permission check passes
    then this spec is put into the request (arg0).  

    If the user is a superuser then the permissions are granted.  If not, the
    file is checked against the user in the request.  A user is only granted
    permission if the file is in under one of "public:users/X" or 
    "private:users/X", where X is the username found in the request.

    The "is_file" parameter is a boolean, True indicates the url is for a file.
    """
    def decorator(target):
        @wraps(target)
        def wrapper(*args, **kwargs):
            # process options
            request = args[0]
            url = request.GET.get(parm)
            if not url:
                raise Http404('permission denied')

            spec = FileSpec.factory_from_url(url, ensure_file=is_file)

            if spec.allowed_for_user(request.user):
                request.spec = spec
                return target(*args, **kwargs)

            logger.error('user %s attempted to access node %s',
                request.user.username, node)

            raise Http404('permission denied')

        return wrapper
    return decorator
