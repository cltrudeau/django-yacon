# yacon.views.settings_tab.py
# blame ctrudeau chr(64) arsensa.com
#
# Views for the Settings tab in Nexus
#

import logging, urllib

from django.http import HttpResponse

from yacon.decorators import superuser_required
from yacon.models.common import Language

logger = logging.getLogger(__name__)

# ============================================================================
# Settings Page Ajax Methods
# ============================================================================

@superuser_required
def add_language(request, name, identifier):
    name = urllib.unquote(name)
    identifier = urllib.unquote(identifier).lower()

    Language.factory(name, identifier)
    return HttpResponse()
