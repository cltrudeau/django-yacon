# yacon.views.user.py
# blame ctrudeau chr(64) arsensa.com

import logging, urllib

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import formats

from django.views.decorators.csrf import csrf_exempt

from yacon.decorators import post_required
from yacon.helpers import prepare_context
from yacon.models.pages import Block, Page
from yacon.utils import JSONResponse

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

    return page.metapage.page_type.render(request, data)

# ============================================================================
# Ajax Views
# ============================================================================

@login_required
@post_required
def replace_block(request):
    """Ajax view for submitting edits to a block."""
    if not request.REQUEST.has_key('block_id'):
        raise Http404('replace_block requires "block_id" parameter')

    if not request.REQUEST.has_key('content'):
        raise Http404('replace_block requires "content" parameter')

    try:
        # block parameter is 'block_X' where X is the id we're after
        block_id = request.POST['block_id'][6:]
        block = Block.objects.get(id=block_id)
    except Block.DoesNotExist:
        raise Http404('no block with id "%s"' % block_id)

    # check permissions
    if not request.user.is_superuser:
        # one of the pages associated with the block must belong to the user
        # logged in 
        pages = block.page_set.filter(owner=request.user)
        if len(pages) == 0:
            raise Http404('permission denied')

    # set the new block content
    block.content = urllib.unquote(request.POST['content'])
    block.save()

    last_updated_list = []
    for page in block.page_set.all():
        when = formats.date_format(page.last_updated, 'DATETIME_FORMAT')
        last_updated_list.append((page.id, when))
    result = {
        'success':True,
        'block_id':block.id,
        'last_updated_list':last_updated_list,
    }
    print '*** result: ', result
    response = JSONResponse(result, extra_headers={'Cache-Control':'no-cache'})
    print '*** response: ', response
    return response


@login_required
@post_required
def replace_title(request):
    """Ajax view for submitting edits to a block."""
    if not request.REQUEST.has_key('page_id'):
        raise Http404('replace_title requires "page_id" parameter')

    if not request.REQUEST.has_key('content'):
        raise Http404('replace_title requires "content" parameter')

    try:
        # page parameter is 'page_X' where X is the id we're after
        page_id = request.POST['page_id'][5:]
        page = Page.objects.get(id=page_id)
    except Page.DoesNotExist:
        raise Http404('no page with id "%s"' % page_id)

    # check permissions
    if not request.user.is_superuser:
        # page must belong to logged in user
        if page.owner != request.user:
            raise Http404('permission denied')

    # set the new block content
    page.title = urllib.unquote(request.POST['content'])
    page.save()

    result = {
        'success':True,
        'last_updated':formats.date_format(page.last_updated, 
            'DATETIME_FORMAT'),
        'page_id':page.id,
    }
    response = JSONResponse(result, extra_headers={'Cache-Control':'no-cache'})
    return response
