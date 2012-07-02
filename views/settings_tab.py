# yacon.views.settings_tab.py
# blame ctrudeau chr(64) arsensa.com
#
# Views for the Settings tab in Nexus
#

import logging, json, urllib
from collections import OrderedDict

from django.db import IntegrityError
from django.conf import settings
from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from yacon.decorators import superuser_required
from yacon.models.common import Language
from yacon.models.hierarchy import (Node, BadSlug, NodeTranslation, Menu,
    MenuItemTranslation)
from yacon.models.site import Site
from yacon.models.pages import MetaPage, Page, PageType, Translation

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
