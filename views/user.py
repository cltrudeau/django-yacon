# yacon.views.user.py
# blame ctrudeau chr(64) arsensa.com

import urllib, logging
from functools import wraps

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse

from yacon.models.site import Site
from yacon.models.pages import Block

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
    site = Site.get_site(request)
    page = site.find_page(uri)
    
    if page == None:
        # no such page found for uri
        raise Http404('CMS did not contain a page for uri: %s' % uri)

    logger.debug('displaying page: %s' % page)
    data = {
        'site':site,
        'page':page,
        'translations':page.other_translations(),
        'request':request,
        'uri':uri,
    }

    if settings.YACON_PAGE_CONTEXT:
        global PAGE_CONTEXT
        if not PAGE_CONTEXT:
            try:
                logger.debug('about to import %s' % settings.YACON_PAGE_CONTEXT)

                fn_name = None
                mod_name = None
                parts = settings.YACON_PAGE_CONTEXT.split('.')
                fn_name = parts[-1]
                mod_name = '.'.join(parts[:-1])

                mod = __import__(mod_name, globals(), locals(), [fn_name])
                logger.debug('mod import successful')

                PAGE_CONTEXT = getattr(mod, fn_name)
            except Exception, e:
                msg = ('importing YACON_PAGE_CONTEXT caused exception, setting:'
                    '"%s", module name:"%s", function name: "%s"' % (
                    settings.YACON_PAGE_CONTEXT, mod_name, fn_name))
                logger.exception(msg)
                raise e

        PAGE_CONTEXT(request, uri, data)

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
