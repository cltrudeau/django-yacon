# yacon.views.user.py
# blame ctrudeau chr(64) arsensa.com

import urllib, logging
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404

from yacon.models.hierarchy import ContentHierarchy
from yacon.models.pages import Page

logger = logging.getLogger(__name__)

# ============================================================================
# Generic Page Display Views
# ============================================================================

def display_page(request, uri):
    """Renders a page corresponding to the uri passed in.  Uses the uri to
    look up a node in the ContentHierarchy and finds a corresponding page.  A
    dictionary of the content blocks is created and passed to the template for
    the page."""
    parsed = ContentHierarchy.parse_path('/' + uri)
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
# Submittal Views
# ============================================================================

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
