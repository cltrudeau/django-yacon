# yacon.views.nexus.py
# blame ctrudeau chr(64) arsensa.com
#
# Nexus is the area for administrators to control the contents of the site,
# permissions, user management etc.  Not named the obvious "admin" to avoid
# conflicts with Django's admin features
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
# Tab Views
# ============================================================================

@superuser_required
def control_panel(request):
    data = {
        'title':'Control Panel',
    }

    return render_to_response('nexus/control_panel.html', data, 
        context_instance=RequestContext(request))


@superuser_required
def config(request):
    langs = Language.objects.all().order_by('identifier')
    data = {
        'title':'Settings',
        'langs':langs,
    }

    return render_to_response('nexus/settings.html', data, 
        context_instance=RequestContext(request))
