# yacon.views.user.py
# blame ctrudeau chr(64) arsensa.com

import urllib, logging
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse

from yacon.models.hierarchy import Site
from yacon.models.pages import Page

logger = logging.getLogger(__name__)

# ============================================================================
# Generic Page Display Views
# ============================================================================

def display_page(request, uri):
    """Default page rendering method for the CMS.  Uses the request object to
    determine what site is being displayed and the uri passed in to find an
    page to render. """
    site = Site.get_site(request)

    parsed = site.parse_path('/' + uri)
    if parsed.node == None:
        # weren't able to parse the path
        raise Http404('Path not found.  Parsed: path=%s' % parsed.path)

    # find the page that corresponds to the uri
    try:
        page = Page.objects.get(node=parsed.node, 
            slug=parsed.slugs_after_node[0])
    except Page.DoesNotExist:
        raise Http404('Page not found for: node=%s, slug=%s' % \
            (parsed.node, parsed.slugs_after_node[0]))

    logger.debug('displaying page: %s' % page)
    data = {}
    data['page'] = page
    data['request'] = request
    data['uri'] = uri
    data['slugs'] = parsed.slugs_after_node

    return render_to_response(page.page_type.template, data, 
        context_instance=RequestContext(request))


# ============================================================================
# Ajax Views
# ============================================================================

def _ajax_preconditions(request):
    """Common code called by ajax_ view methods"""
    if request.method != 'POST':
        raise Http404('GET method not supported for ajax_submit')

    if not request.REQUEST.has_key('block_id'):
        raise Http404('ajax_submit requires "block_id" parameter')

    try:
        # find the block corresponding to the id passed in
        block = Block.objects.get(pk=request.POST['block_id'])
    except:
        raise Http404( 'no block with id "%s"' % request.POST['block'])

    return block


def ajax_display(request):
    block = _ajax_preconditions(request)

    return HttpResponse(block.render( ))


def ajax_submit(request):
    """Used for submitting user generated content to the system"""

    if request.method != 'POST':
        raise Http404('GET method not supported for ajax_submit')

    if not request.REQUEST.has_key('block_id'):
        raise Http404('ajax_submit requires "block_id" parameter')

    # ok, we've got the page, now get the block name
    try:
        block = Block.objects.get(pk=request.POST['block_id'])
    except:
        raise Http404( 'no block with id "%s"' % request.POST['block'])

    # set the new block content
    block.content = urllib.unquote(request.POST['content'])
    block.save()

    response = render_to_response('block_response.html', data, 
        context_instance=RequestContext(request))
    response['Cache-Control'] = 'no-cache'
    return response
