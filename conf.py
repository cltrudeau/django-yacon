# yacon.conf.py
import logging

from django.conf import settings

from yacon.loaders import dynamic_load, dynamic_safe_load

logger = logging.getLogger(__name__)

# ============================================================================
# Default Configuration Settings

SITE = {
    'static_serve':False,
    'ajax_edit_enabled':False,
    'tests_enabled':False,
    'examples_enabled':False,
    'local_jquery':False,
    'custom_enabled':True,
    'private_upload':None,
    'private_upload_url':None,
    'auto_thumbnails':{},
    'image_extensions':['jpg', 'jpeg', 'png', 'gif'],
}

NEXUS = {
    'enabled':True,
    'add_site_disabled':False,
}

CUSTOM = {
    # 'page_context' handled specially
    # 'user_curator' handled specially
    'extra_admin_nav':[],
}

# ============================================================================

def _fetch_setting(group, key):
    if hasattr(settings, 'YACON'):
        try:
            return settings.YACON[group][key]
        except KeyError:
            # either group or key wasn't there, do nothing and proceed to the
            # defaults
            pass

    # find a default value, either YACON wasn't in settings or it didn't have
    # an overridding key
    try:
        if group == 'site':
            return SITE[key]
        elif group == 'nexus':
            return NEXUS[key]
        elif group == 'custom':
            return CUSTOM[key]
        else:
            logger.error('bad group "%s" requested from yacon.conf')

    except KeyError:
        # bad key, do nothing
        pass

    return None


def _site(key):
    return _fetch_setting('site', key)


def _nexus(key):
    return _fetch_setting('nexus', key)


_PAGE_CONTEXT = None
_USER_CURATOR = None

def _custom(key):
    global _PAGE_CONTEXT, _USER_CURATOR

    custom_enabled = _fetch_setting('site', 'custom_enabled')
    value = _fetch_setting('custom', key)

    if key == 'page_context':
        if value and custom_enabled:
            # settings has overridden the page context, load it dynamically if
            # it  isn't already
            if not _PAGE_CONTEXT:
                _PAGE_CONTEXT = dynamic_safe_load(value,
                    'yacon.custom.page_context', None)
        else:
            # default page context
            _PAGE_CONTEXT = lambda x, y, z: ''

        return _PAGE_CONTEXT
    elif key == 'user_curator':
        if value and custom_enabled:
            # settings has overridden the curator, singleton load it
            if not _USER_CURATOR:
                _USER_CURATOR = dynamic_load(value)
        else:
            # default curator, singleton load it
            if not _USER_CURATOR:
                _USER_CURATOR = dynamic_load('yacon.curators.UserCurator')

        return _USER_CURATOR

    # else:
    return value

# ============================================================================
# Conf 

class Conf(object):
    def __init__(self, fn):
        self.fn = fn

    def __getattr__(self, key):
        value = self.fn(key)
        return value

site = Conf(_site)
nexus = Conf(_nexus)
custom = Conf(_custom)
