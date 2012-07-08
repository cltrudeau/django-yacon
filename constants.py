# yacon.constants.py

import logging

from django.conf import settings

from yacon.loaders import dynamic_load, dynamic_safe_load

logger = logging.getLogger(__name__)

# ============================================================================

# Page Context: function called to add context to user defined views
PAGE_CONTEXT = None
if hasattr(settings, 'YACON_PAGE_CONTEXT'):
    PAGE_CONTEXT = dynamic_safe_load(settings.YACON_PAGE_CONTEXT,
        'YACON_PAGE_CONTEXT', None)


# User Curator: proxy & factory class for dealing with user defined
#               UserProfile objects
if hasattr(settings, 'YACON_USER_CURATOR'):
    USER_CURATOR = dynamic_load(settings.YACON_USER_CURATOR)
else:
    USER_CURATOR = dynamic_load('yacon.curators.UserCurator')
