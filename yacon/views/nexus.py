# yacon.views.nexus.py
#
# Nexus is the area for administrators to control the contents of the site,
# permissions, user management etc.  Not named the obvious "admin" to avoid
# conflicts with Django's admin features
#

import logging

from django.template import RequestContext
from django.shortcuts import render_to_response

from yacon.decorators import superuser_required
from yacon.models.common import Language

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
def config_panel(request):
    langs = Language.objects.all().order_by('identifier')
    data = {
        'title':'Settings',
        'langs':langs,
    }

    return render_to_response('nexus/config_panel.html', data, 
        context_instance=RequestContext(request))


# users_panel redirects straight to list_users


@superuser_required
def uploads_panel(request):
    data = {
        'title':'Uploads',
        'base_template':'nexus_base.html',
        'choose_mode':'view',
        'popup':False,
    }
    request.session['choose_mode'] = 'view'
    request.session['image_only'] = False
    request.session['popup'] = False

    return render_to_response('browser/browser.html', data, 
        context_instance=RequestContext(request))
