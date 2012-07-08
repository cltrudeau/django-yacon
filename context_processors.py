# yacon.context_processors.py
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# =============================================================================

def processor(request):
    data = {
        'admin_enabled': 'django.contrib.admin' in settings.INSTALLED_APPS,
        'settings':settings,
    }

    if hasattr(request, 'user'):
        data['user'] = request.user
        if request.user.is_authenticated():
            data['authenticated'] = True
            if request.user.is_superuser:
                data['superuser'] = True

    return data
