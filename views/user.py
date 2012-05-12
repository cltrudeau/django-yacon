# yacon.views.user.py
# blame ctrudeau chr(64) arsensa.com

import urllib, logging
from functools import wraps

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse

from yacon.models.site import Site
from yacon.models.pages import Block

logger = logging.getLogger(__name__)

# ============================================================================
# Generic Page Display Views
# ============================================================================

def display_page(request, uri=''):
    """Default page rendering method for the CMS.  Uses the request object to
    determine what site is being displayed and the uri passed in to find an
    page to render. """
    site = Site.get_site(request)
    page = site.find_page(uri)
    
    if page == None:
        # no such page found for uri
        raise Http404('CMS did not contain a page for uri: %s' % uri)

    logger.debug('displaying page: %s' % page)
    data = {}
    data['page'] = page
    data['translations'] = page.other_translations()
    data['request'] = request
    data['uri'] = uri

    return render_to_response(page.metapage.page_type.template, data, 
        context_instance=RequestContext(request))

# ============================================================================
# Ajax Views
# ============================================================================

def ajax_preconditions(target):
    """Preconditions on ajax method calls.  Checks that it is a POST and has
    the appropriate fields.  Puts the block involved in the call into the
    request object."""

    @wraps(target)
    def wrapper(*args, **kwargs):
        request = args[0]
        if request.method != 'POST':
            raise Http404('GET method not supported for ajax_submit')

        print request.POST
        if not request.REQUEST.has_key('block_id'):
            raise Http404('ajax_submit requires "block_id" parameter')

        if not request.REQUEST.has_key('content'):
            raise Http404('ajax_submit requires "content" parameter')

        try:
            # find the block corresponding to the id passed in
            block = Block.objects.get(pk=request.POST['block_id'])
            request.block = block
            return target(*args, **kwargs)
        except:
            raise Http404( 'no block with id "%s"' % request.POST['block'])

    return wrapper


#@login_required
@ajax_preconditions
def ajax_submit(request):
    """Used for submitting user generated content to the system"""

    # set the new block content
    request.block.content = urllib.unquote(request.POST['content'])
    request.block.save()

    response = HttpResponse('{"success":"true"}')
    response['Cache-Control'] = 'no-cache'
    return response
