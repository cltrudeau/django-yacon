# yacon.views.user.py
# blame ctrudeau chr(64) arsensa.com

import urllib, logging
from functools import wraps

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse

from yacon.decorators import superuser_required
from yacon.models.site import Site
from yacon.models.pages import Block
from yacon.utils import prepare_context

logger = logging.getLogger(__name__)

# ============================================================================
# Constants

PAGE_CONTEXT = None

# ============================================================================
# Generic Page Display Views
# ============================================================================

def display_page(request, uri=''):
    """Default page rendering method for the CMS.  Uses the request object to
    determine what site is being displayed and the uri passed in to find an
    page to render. """
    data = prepare_context(request, uri)
    page = data['site'].find_page(uri)
    
    if page == None:
        # no such page found for uri
        raise Http404('CMS did not contain a page for uri: %s' % uri)

    data.update({
        'page':page,
        'translations':page.other_translations(),
    })

    return render_to_response(page.metapage.page_type.template, data, 
        context_instance=RequestContext(request))
