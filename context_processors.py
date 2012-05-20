# yacon.context_processors.py

import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# =============================================================================

def globals(request):
    data = {
        'admin_enabled': 'django.contrib.admin' in settings.INSTALLED_APPS,
    }

    return data
