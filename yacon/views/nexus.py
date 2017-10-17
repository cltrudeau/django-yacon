# yacon.views.nexus.py
#
# Nexus is the area for administrators to control the contents of the site,
# permissions, user management etc.  Not named the obvious "admin" to avoid
# conflicts with Django's admin features
#

import logging

from django.shortcuts import render

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

    return render(request, 'yacon/nexus/control_panel.html', data)


@superuser_required
def config_panel(request):
    langs = Language.objects.all().order_by('identifier')
    data = {
        'title':'Settings',
        'langs':langs,
    }

    return render(request, 'yacon/nexus/config_panel.html', data)


# users_panel redirects straight to list_users


@superuser_required
def uploads_panel(request):
    data = {
        'title':'Uploads',
        'base_template':'yacon/nexus_base.html',
        'choose_mode':'view',
        'popup':False,
    }
    request.session['choose_mode'] = 'view'
    request.session['image_only'] = False
    request.session['popup'] = False

    return render(request, 'yacon/browser/browser.html', data)
